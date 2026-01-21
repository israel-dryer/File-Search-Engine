"""
Test Benchmark Module

Tests for the benchmark_models module including metric calculations
and result generation.
"""

import unittest
import os
from unittest.mock import patch, MagicMock


class TestBenchmarkModels(unittest.TestCase):
    """Tests for benchmark_models module."""
    
    def test_import_benchmark_module(self):
        """Test that benchmark_models module can be imported."""
        try:
            from scripts import benchmark_models
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import benchmark_models: {e}")
    
    def test_benchmark_result_dataclass(self):
        """Test BenchmarkResult class structure."""
        from scripts.benchmark_models import BenchmarkResult
        
        result = BenchmarkResult(model_name="test-model")
        
        self.assertEqual(result.model_name, "test-model")
        self.assertIsNotNone(result.embedding_latency_ms)
        self.assertIsNotNone(result.tokens_per_second)
    
    def test_get_memory_usage(self):
        """Test memory usage monitoring function."""
        from scripts.benchmark_models import get_memory_usage_mb
        
        memory = get_memory_usage_mb()
        
        self.assertIsInstance(memory, (int, float))
        self.assertGreater(memory, 0, "Memory usage should be positive")
    
    def test_calculate_fact_retention(self):
        """Test fact retention score calculation."""
        from scripts.benchmark_models import calculate_fact_retention
        
        key_concepts = ["Python", "programming", "data science"]
        summary = "Python programming language is used for data science"
        
        score = calculate_fact_retention(summary, key_concepts)
        
        self.assertIsInstance(score, (int, float))
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)
    
    def test_fact_retention_perfect_match(self):
        """Test fact retention when summary contains all key concepts."""
        from scripts.benchmark_models import calculate_fact_retention
        
        key_concepts = ["machine learning", "artificial intelligence", "data"]
        summary = "machine learning and artificial intelligence uses data"
        
        score = calculate_fact_retention(summary, key_concepts)
        
        # Should be high score since all keywords are present (100%)
        self.assertEqual(score, 100.0)
    
    def test_fact_retention_no_match(self):
        """Test fact retention when summary is completely different."""
        from scripts.benchmark_models import calculate_fact_retention
        
        key_concepts = ["machine learning", "artificial intelligence"]
        summary = "cooking recipes and gardening tips"
        
        score = calculate_fact_retention(summary, key_concepts)
        
        # Should be 0 since no keywords match
        self.assertEqual(score, 0.0)
    
    def test_benchmark_result_to_dict(self):
        """Test BenchmarkResult conversion to dictionary."""
        from scripts.benchmark_models import BenchmarkResult
        
        result = BenchmarkResult(model_name="test-model")
        result.embedding_latency_ms = 50.0
        result.tokens_per_second = 25.0
        result.fact_retention_score = 85.0
        result.peak_memory_mb = 1024.0
        result.load_time_s = 3.5
        result.first_token_latency_ms = 100.0
        
        result_dict = result.to_dict()
        
        self.assertIsInstance(result_dict, dict)
        self.assertEqual(result_dict['model_name'], "test-model")
        self.assertEqual(result_dict['embedding_latency_ms'], 50.0)
        self.assertEqual(result_dict['tokens_per_second'], 25.0)


class TestBenchmarkSamples(unittest.TestCase):
    """Tests for benchmark sample data."""
    
    def test_test_samples_exist(self):
        """Test that TEST_SAMPLES are defined."""
        from scripts.benchmark_models import TEST_SAMPLES
        
        self.assertIsInstance(TEST_SAMPLES, list)
        self.assertGreater(len(TEST_SAMPLES), 0)
    
    def test_test_samples_structure(self):
        """Test that TEST_SAMPLES have correct structure."""
        from scripts.benchmark_models import TEST_SAMPLES
        
        for sample in TEST_SAMPLES:
            self.assertIn('id', sample)
            self.assertIn('name', sample)
            self.assertIn('text', sample)
            self.assertIn('key_concepts', sample)
            self.assertIsInstance(sample['text'], str)
            self.assertGreater(len(sample['text']), 10)
    
    def test_test_queries_exist(self):
        """Test that TEST_QUERIES are defined."""
        from scripts.benchmark_models import TEST_QUERIES
        
        self.assertIsInstance(TEST_QUERIES, list)
        self.assertGreater(len(TEST_QUERIES), 0)


class TestBenchmarkIntegration(unittest.TestCase):
    """Integration tests for benchmark module."""
    
    def test_get_local_models(self):
        """Test that get_local_models returns list of models."""
        from scripts.benchmark_models import get_local_models
        
        models = get_local_models()
        
        self.assertIsInstance(models, list)
        
        # If models exist, check structure
        for model in models:
            self.assertIn('name', model)
            self.assertIn('path', model)
            self.assertIn('size_mb', model)


if __name__ == '__main__':
    unittest.main(verbosity=2)
