"""
Test Model Manager

Tests for the model_manager module including model downloads,
resource checks, and model discovery.
"""

import unittest
import os
from unittest.mock import patch, MagicMock


class TestModelManager(unittest.TestCase):
    """Tests for model_manager module."""
    
    def test_get_available_models(self):
        """Test that available models list is returned."""
        from backend.model_manager import get_available_models
        
        models = get_available_models()
        
        self.assertIsInstance(models, list)
        self.assertGreater(len(models), 0, "No available models defined")
        
        # Check model structure
        for model in models:
            self.assertIn('id', model)
            self.assertIn('name', model)
            self.assertIn('url', model)
            self.assertIn('size', model)
    
    def test_model_metadata_complete(self):
        """Test that all models have required metadata."""
        from backend.model_manager import get_available_models
        
        models = get_available_models()
        required_fields = ['id', 'name', 'description', 'size', 'ram_required', 'category', 'url']
        
        for model in models:
            for field in required_fields:
                with self.subTest(model=model['id'], field=field):
                    self.assertIn(field, model, f"Model {model['id']} missing {field}")
    
    def test_model_categories(self):
        """Test that models are properly categorized."""
        from backend.model_manager import get_available_models
        
        models = get_available_models()
        valid_categories = ['small', 'medium', 'large', 'premium', 'extra-large']
        
        for model in models:
            with self.subTest(model=model['id']):
                self.assertIn(
                    model.get('category'), 
                    valid_categories,
                    f"Model {model['id']} has invalid category"
                )
    
    def test_get_local_models(self):
        """Test discovering locally downloaded models."""
        from backend.model_manager import get_local_models
        
        local_models = get_local_models()
        
        self.assertIsInstance(local_models, list)
        
        # If we have models, check structure
        for model in local_models:
            self.assertIn('id', model)
            self.assertIn('path', model)
            self.assertIn('size', model)
            self.assertTrue(os.path.exists(model['path']), f"Model path doesn't exist: {model['path']}")
    
    def test_check_system_resources(self):
        """Test system resource checking function."""
        from backend.model_manager import check_system_resources
        
        test_model = {
            'id': 'test-model',
            'size_bytes': 1000000,  # 1MB - should always have enough space
            'ram_required': 1  # 1GB - should always have enough
        }
        
        can_download, warnings = check_system_resources(test_model)
        
        self.assertIsInstance(can_download, bool)
        self.assertIsInstance(warnings, list)
    
    def test_check_system_resources_large_model(self):
        """Test resource check rejects models too large for system."""
        from backend.model_manager import check_system_resources
        
        # Model requiring 1TB - definitely too large
        test_model = {
            'id': 'impossible-model',
            'size_bytes': 1000 * 1024 * 1024 * 1024,  # 1TB
            'ram_required': 500  # 500GB RAM
        }
        
        can_download, warnings = check_system_resources(test_model)
        
        self.assertFalse(can_download, "Should reject model requiring 1TB disk space")
        self.assertGreater(len(warnings), 0, "Should have warnings")
    
    def test_get_download_status(self):
        """Test download status retrieval."""
        from backend.model_manager import get_download_status
        
        status = get_download_status()
        
        self.assertIsInstance(status, dict)
        self.assertIn('downloading', status)
        self.assertIn('progress', status)
    
    @patch('backend.model_manager.requests.get')
    def test_download_nonexistent_model(self, mock_get):
        """Test downloading a non-existent model ID fails gracefully."""
        from backend.model_manager import start_download
        
        success, message = start_download('nonexistent-model-id')
        
        self.assertFalse(success)
        self.assertIn('not found', message.lower())


class TestModelManagerIntegration(unittest.TestCase):
    """Integration tests for model manager with real files."""
    
    def setUp(self):
        """Set up test environment."""
        from backend.model_manager import MODELS_DIR
        self.models_dir = MODELS_DIR
    
    def test_models_directory_exists(self):
        """Test that models directory exists."""
        self.assertTrue(
            os.path.exists(self.models_dir),
            f"Models directory should exist at {self.models_dir}"
        )
    
    def test_local_models_match_files(self):
        """Test that get_local_models returns actual files."""
        from backend.model_manager import get_local_models
        
        local_models = get_local_models()
        
        # Check that each returned model actually exists
        for model in local_models:
            self.assertTrue(
                os.path.exists(model['path']),
                f"Returned model path doesn't exist: {model['path']}"
            )
    
    def test_local_model_sizes_accurate(self):
        """Test that reported model sizes match actual file sizes."""
        from backend.model_manager import get_local_models
        
        local_models = get_local_models()
        
        for model in local_models:
            actual_size = os.path.getsize(model['path'])
            reported_size = model['size']
            
            self.assertEqual(
                actual_size, reported_size,
                f"Size mismatch for {model['id']}: reported {reported_size}, actual {actual_size}"
            )


if __name__ == '__main__':
    unittest.main(verbosity=2)
