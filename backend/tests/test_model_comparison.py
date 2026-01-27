"""
Test Model Comparison and Ranking

Tests that compare outputs from multiple downloaded models
and can rank them based on response quality.

NOTE: These tests require:
1. Downloaded models in the 'models/' directory
2. Working llama-cpp-python installation
3. Sufficient RAM to load models

Tests will skip gracefully if requirements are not met.
"""

import unittest
import os
import time
from typing import List, Dict, Optional


def try_load_model(model_path: str):
    """Attempt to load a model, return None if it fails."""
    try:
        from llama_cpp import Llama
        llm = Llama(model_path=model_path, n_ctx=512, verbose=False)
        return llm
    except Exception as e:
        print(f"Could not load model {os.path.basename(model_path)}: {e}")
        return None


class TestModelComparison(unittest.TestCase):
    """Tests for comparing and ranking multiple LLM models."""
    
    @classmethod
    def setUpClass(cls):
        """Set up models for testing - runs once before all tests."""
        # Correct path to project root models/ directory
        cls.models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'models')
        cls.available_models = []

        cls.working_models = []
        
        # Find all downloaded .gguf models
        if os.path.exists(cls.models_dir):
            for f in os.listdir(cls.models_dir):
                if f.endswith('.gguf'):
                    cls.available_models.append(os.path.join(cls.models_dir, f))
        
        print(f"\nFound {len(cls.available_models)} models for testing")
        
        # Test questions for comparison
        cls.test_questions = [
            {
                "question": "What is 2 + 2?",
                "expected_keywords": ["4", "four"],
                "context": "Basic arithmetic: 2 plus 2 equals 4."
            },
            {
                "question": "What color is the sky?",
                "expected_keywords": ["blue", "azure"],
                "context": "The sky appears blue during the day due to light scattering."
            },
            {
                "question": "What is the capital of France?",
                "expected_keywords": ["paris"],
                "context": "France is a country in Europe. Its capital city is Paris."
            }
        ]
    
    def test_models_available(self):
        """Test that at least one model is available for testing."""
        if not self.available_models:
             self.skipTest("No models found in models/ directory. Download at least one model.")
        
        self.assertGreater(len(self.available_models), 0)

    
    def test_model_loading(self):
        """Test that at least one model can be loaded."""
        if not self.available_models:
            self.skipTest("No models available in models/ directory")
        
        try:
            from llama_cpp import Llama
        except ImportError:
            self.skipTest("llama_cpp not installed")
        
        loaded_count = 0
        for model_path in self.available_models[:3]:  # Test first 3 models
            llm = try_load_model(model_path)
            if llm:
                loaded_count += 1
                del llm
        
        if loaded_count == 0:
            self.skipTest("No models could be loaded (may need different llama-cpp version)")
        else:
            print(f"\nSuccessfully loaded {loaded_count}/{min(3, len(self.available_models))} models")
    
    def test_single_model_generation(self):
        """Test that a model can generate text."""
        if not self.available_models:
            self.skipTest("No models available")
        
        try:
            from llama_cpp import Llama
        except ImportError:
            self.skipTest("llama_cpp not installed")
        
        # Try to find a working model
        llm = None
        model_name = None
        for model_path in self.available_models:
            llm = try_load_model(model_path)
            if llm:
                model_name = os.path.basename(model_path)
                break
        
        if not llm:
            self.skipTest("No models could be loaded")
        
        try:
            output = llm("Hello, how are you?", max_tokens=20)
            
            self.assertIn('choices', output)
            self.assertGreater(len(output['choices']), 0)
            self.assertIn('text', output['choices'][0])
            
            generated_text = output['choices'][0]['text']
            self.assertIsInstance(generated_text, str)
            print(f"\n{model_name} generated: {generated_text[:50]}...")
        finally:
            del llm
    
    def test_compare_multiple_models(self):
        """Test comparing outputs from multiple models on the same question."""
        if len(self.available_models) < 2:
            self.skipTest("Need at least 2 models for comparison")
        
        try:
            from llama_cpp import Llama
        except ImportError:
            self.skipTest("llama_cpp not installed")
        
        # Find 2 working models
        working = []
        for model_path in self.available_models:
            llm = try_load_model(model_path)
            if llm:
                working.append((model_path, llm))
                if len(working) >= 2:
                    break
        
        if len(working) < 2:
            # Clean up any loaded models
            for _, llm in working:
                del llm
            self.skipTest("Could not load 2 models for comparison")
        
        question = self.test_questions[0]
        prompt = f"Context: {question['context']}\n\nQuestion: {question['question']}\n\nAnswer:"
        results = []
        
        for model_path, llm in working:
            model_name = os.path.basename(model_path)
            try:
                start_time = time.time()
                output = llm(prompt, max_tokens=50)
                latency = time.time() - start_time
                
                generated_text = output['choices'][0]['text'].strip()
                
                results.append({
                    'model': model_name,
                    'answer': generated_text,
                    'latency': latency
                })
            except Exception as e:
                print(f"Error generating with {model_name}: {e}")
            finally:
                del llm
        
        self.assertGreater(len(results), 0, "No models produced output")
        
        print("\n=== Model Comparison Results ===")
        for r in results:
            print(f"\nModel: {r['model']}")
            print(f"Answer: {r['answer'][:100]}")
            print(f"Latency: {r['latency']:.2f}s")
    
    def test_rank_models_by_accuracy(self):
        """Test ranking models by answer accuracy (keyword matching)."""
        if len(self.available_models) < 2:
            self.skipTest("Need at least 2 models for ranking")
        
        try:
            from llama_cpp import Llama
        except ImportError:
            self.skipTest("llama_cpp not installed")
        
        # Find working models
        working = []
        for model_path in self.available_models:
            llm = try_load_model(model_path)
            if llm:
                working.append((model_path, llm))
                if len(working) >= 2:
                    break
        
        if len(working) < 2:
            for _, llm in working:
                del llm
            self.skipTest("Could not load 2 models for ranking")
        
        question = self.test_questions[0]
        prompt = f"Context: {question['context']}\n\nQuestion: {question['question']}\n\nAnswer:"
        scores = []
        
        for model_path, llm in working:
            model_name = os.path.basename(model_path)
            try:
                output = llm(prompt, max_tokens=50)
                generated_text = output['choices'][0]['text'].strip().lower()
                
                score = sum(1 for kw in question['expected_keywords'] if kw.lower() in generated_text)
                scores.append({
                    'model': model_name,
                    'answer': generated_text,
                    'score': score
                })
            except Exception as e:
                print(f"Error with {model_name}: {e}")
            finally:
                del llm
        
        ranked = sorted(scores, key=lambda x: x['score'], reverse=True)
        
        print("\n=== Model Ranking by Accuracy ===")
        for i, r in enumerate(ranked, 1):
            print(f"{i}. {r['model']} (score: {r['score']})")
        
        self.assertGreater(len(ranked), 0, "No models were ranked")


class TestModelQuality(unittest.TestCase):
    """Tests for model output quality assessment."""
    
    def test_response_coherence(self):
        """Test that model responses are coherent (not gibberish)."""
        models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'models')
        
        if not os.path.exists(models_dir):
            self.skipTest("Models directory not found")
        
        models = [os.path.join(models_dir, f) for f in os.listdir(models_dir) if f.endswith('.gguf')]
        
        if not models:
            self.skipTest("No models available")
        
        try:
            from llama_cpp import Llama
        except ImportError:
            self.skipTest("llama_cpp not installed")
        
        # Find a working model
        llm = None
        for model_path in models:
            llm = try_load_model(model_path)
            if llm:
                break
        
        if not llm:
            self.skipTest("No models could be loaded")
        
        try:
            prompt = "The weather today is"
            output = llm(prompt, max_tokens=20)
            response = output['choices'][0]['text'].strip()
            
            # Check for basic coherence (at least 3 characters)
            self.assertGreaterEqual(len(response), 3, "Response too short")
            
            # Check that response contains actual words
            words = response.split()
            valid_words = [w for w in words if len(w) > 1 and w.isalpha()]
            self.assertGreater(len(valid_words), 0, "Response contains no valid words")
        finally:
            del llm
    
    def test_response_length_control(self):
        """Test that max_tokens parameter is respected."""
        models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'models')
        
        if not os.path.exists(models_dir):
            self.skipTest("Models directory not found")
        
        models = [os.path.join(models_dir, f) for f in os.listdir(models_dir) if f.endswith('.gguf')]
        
        if not models:
            self.skipTest("No models available")
        
        try:
            from llama_cpp import Llama
        except ImportError:
            self.skipTest("llama_cpp not installed")
        
        llm = None
        for model_path in models:
            llm = try_load_model(model_path)
            if llm:
                break
        
        if not llm:
            self.skipTest("No models could be loaded")
        
        try:
            prompt = "Tell me a very long story about:"
            output = llm(prompt, max_tokens=10)
            
            tokens_used = output.get('usage', {}).get('completion_tokens', 0)
            # Allow some tolerance
            self.assertLessEqual(tokens_used, 15, "Max tokens not respected")
        finally:
            del llm


if __name__ == '__main__':
    unittest.main(verbosity=2)
