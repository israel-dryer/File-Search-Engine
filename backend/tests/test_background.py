import unittest
import tempfile
import os
from unittest.mock import patch, MagicMock
from backend.background import start_background_indexing, IndexingEventHandler


class TestBackground(unittest.TestCase):
    """Test cases for background module"""

    @patch('backend.background.save_index')
    def test_indexing_event_handler_initialization(self, mock_save_index):
        """Test initialization of IndexingEventHandler."""
        with patch('backend.background.create_index') as mock_create_index:
            mock_create_index.return_value = (MagicMock(), ["doc1"], ["tag1"], None, None, None, None)
            
            handler = IndexingEventHandler(
                folder="/test/folder",
                provider="openai",
                api_key="test_key",
                model_path=None
            )
            
            # Verify attributes are set correctly
            self.assertEqual(handler.folder, "/test/folder")
            self.assertEqual(handler.provider, "openai")
            self.assertEqual(handler.api_key, "test_key")
            self.assertIsNone(handler.model_path)
            
            # Verify update_index was NOT called during initialization
            mock_create_index.assert_not_called()
            mock_save_index.assert_not_called()
    
    @patch('backend.background.create_index')
    @patch('backend.background.save_index')
    def test_update_index(self, mock_save_index, mock_create_index):
        """Test the update_index method of IndexingEventHandler."""
        mock_index = MagicMock()
        mock_create_index.return_value = (mock_index, ["doc1"], ["tag1"], None, None, None, None)
        
        handler = IndexingEventHandler(
            folder="/test/folder",
            provider="openai",
            api_key="test_key",
            model_path=None
        )
        
        # Call update_index directly
        handler.update_index()
        
        # Verify create_index was called
        mock_create_index.assert_called_once_with(
            "/test/folder", "openai", "test_key", None
        )
        
        # Verify save_index was called
        mock_save_index.assert_called_once_with(
            mock_index, ["doc1"], ["tag1"], 'index.faiss', None, None, None, None
        )
    
    @patch('backend.background.create_index')
    def test_update_index_none_result(self, mock_create_index):
        """Test update_index when create_index returns None."""
        mock_create_index.return_value = (None, None, None, None, None, None, None)
        
        handler = IndexingEventHandler(
            folder="/test/folder",
            provider="openai",
            api_key="test_key",
            model_path=None
        )
        
        # Call update_index directly
        handler.update_index()
        
        # Verify create_index was called but save_index was not
        mock_create_index.assert_called_once_with(
            "/test/folder", "openai", "test_key", None
        )
    
    @patch('backend.background.create_index')
    @patch('backend.background.save_index')
    def test_on_modified_triggers_update(self, mock_save_index, mock_create_index):
        """Test that on_modified event triggers index update."""
        mock_index = MagicMock()
        mock_create_index.return_value = (mock_index, ["doc1"], ["tag1"], None, None, None, None)
        
        handler = IndexingEventHandler(
            folder="/test/folder",
            provider="openai",
            api_key="test_key",
            model_path=None
        )
        
        # Simulate on_modified event
        event = MagicMock()
        handler.on_modified(event)
        
        # Verify create_index was called
        mock_create_index.assert_called_once()
        mock_save_index.assert_called_once()
    
    @patch('backend.background.create_index')
    @patch('backend.background.save_index')
    def test_on_created_triggers_update(self, mock_save_index, mock_create_index):
        """Test that on_created event triggers index update."""
        mock_index = MagicMock()
        mock_create_index.return_value = (mock_index, ["doc1"], ["tag1"], None, None, None, None)
        
        handler = IndexingEventHandler(
            folder="/test/folder",
            provider="openai",
            api_key="test_key",
            model_path=None
        )
        
        # Simulate on_created event
        event = MagicMock()
        handler.on_created(event)
        
        # Verify create_index was called
        mock_create_index.assert_called_once()
        mock_save_index.assert_called_once()
    
    @patch('backend.background.create_index')
    @patch('backend.background.save_index')
    def test_on_deleted_triggers_update(self, mock_save_index, mock_create_index):
        """Test that on_deleted event triggers index update."""
        mock_index = MagicMock()
        mock_create_index.return_value = (mock_index, ["doc1"], ["tag1"], None, None, None, None)
        
        handler = IndexingEventHandler(
            folder="/test/folder",
            provider="openai",
            api_key="test_key",
            model_path=None
        )
        
        # Simulate on_deleted event
        event = MagicMock()
        handler.on_deleted(event)
        
        # Verify create_index was called
        mock_create_index.assert_called_once()
        mock_save_index.assert_called_once()


if __name__ == '__main__':
    unittest.main()
