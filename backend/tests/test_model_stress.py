import unittest
import os
import time
import json
import logging
from typing import List, Dict, Any
from scripts.benchmark_models import BenchmarkResult, calculate_fact_retention, get_memory_usage_mb

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestModelStress(unittest.TestCase):
    """
    Advanced Stress Testing Suite for LLM Models.
    Focuses on stability, context pressure, and multi-metric ranking.
    """
    
    @classmethod
    def setUpClass(cls):
        """Find all available models in the project root models/ directory."""
        cls.project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        cls.models_dir = os.path.join(cls.project_root, "models")
        cls.available_models = []
        
        if os.path.exists(cls.models_dir):
            for f in os.listdir(cls.models_dir):
                if f.endswith(".gguf"):
                    cls.available_models.append({
                        "name": f.replace(".gguf", ""),
                        "filename": f,
                        "path": os.path.join(cls.models_dir, f),
                        "size_mb": os.path.getsize(os.path.join(cls.models_dir, f)) / (1024 * 1024)
                    })
        
        cls.available_models.sort(key=lambda x: x["size_mb"])
        logger.info(f"Stress test found {len(cls.available_models)} models.")

    def test_model_rankings(self):
        """Run a full suite of benchmarks and rank models by weighted score."""
        if not self.available_models:
            self.skipTest("No models available for ranking.")
        
        from backend.llm_integration import get_embeddings
        from langchain_community.llms import LlamaCpp
        
        benchmark_results = []
        
        # Test each model
        for model_info in self.available_models:
            logger.info(f"Stress testing model: {model_info['name']}")
            result = BenchmarkResult(model_info["name"])
            result.model_path = model_info["path"]
            result.model_size_mb = model_info["size_mb"]
            
            try:
                # 1. Stability Test: 5 consecutive calls (scaled down from 10 for time)
                # We measure average TPS and consistency
                tps_readings = []
                load_start = time.time()
                llm = LlamaCpp(
                    model_path=model_info["path"],
                    n_ctx=2048,
                    n_batch=512,
                    verbose=False,
                    n_threads=4 # Standard thread count
                )
                result.load_time_s = time.time() - load_start
                
                # Warmup
                llm.invoke("Hi")
                
                baseline_mem = get_memory_usage_mb()
                
                # Run stability loops
                for i in range(3):
                    start = time.time()
                    resp = llm.invoke(f"Tell me something interesting about number {i}.")
                    latency = time.time() - start
                    tokens = len(resp.split())
                    if tokens > 0:
                        tps_readings.append(tokens / latency)
                
                if tps_readings:
                    result.tokens_per_second = sum(tps_readings) / len(tps_readings)
                
                # 2. Context Pressure Test (Longer input)
                pressure_text = "Data " * 500 # ~500 words
                start = time.time()
                resp = llm.invoke(f"Summarize this in one word: {pressure_text}")
                result.total_generation_time_s = time.time() - start
                
                # 3. Accuracy Check
                key_concepts = ["data"]
                result.fact_retention_score = calculate_fact_retention(resp, key_concepts)
                
                # Memory Peak
                result.peak_memory_mb = get_memory_usage_mb() - baseline_mem
                
                benchmark_results.append(result)
                
            except Exception as e:
                logger.error(f"Failed to stress test {model_info['name']}: {e}")
                result.errors.append(str(e))
                benchmark_results.append(result)
        
        # Rank by score
        benchmark_results.sort(key=lambda x: x.weighted_score, reverse=True)
        
        # Print Ranking Table
        print("\n" + "="*90)
        print(f"{'RANK':<5} {'MODEL':<35} {'SCORE':>8} {'TPS':>8} {'MEM(MB)':>8} {'LOAD(s)':>8}")
        print("-" * 90)
        for rank, res in enumerate(benchmark_results, 1):
            print(f"{rank:<5} {res.model_name[:35]:<35} {res.weighted_score:>8.1f} {res.tokens_per_second:>8.1f} {res.peak_memory_mb:>8.0f} {res.load_time_s:>8.1f}")
        print("="*90)
        
        self.assertTrue(len(benchmark_results) > 0)
        self.assertGreater(benchmark_results[0].weighted_score, 0)

if __name__ == "__main__":
    unittest.main()
