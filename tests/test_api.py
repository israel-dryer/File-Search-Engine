import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from api import app

class TestAPI(unittest.TestCase):
    """Test cases for API module"""

    def setUp(self):
        """Set up test client before each test method."""
        self.client = TestClient(app)
    
    @patch('api.load_config')
    def test_get_config(self, mock_load_config):
        """Test getting configuration."""
        mock_config = MagicMock()
        mock_config.get.side_effect = lambda section, key, fallback='': {
            ('General', 'folder'): '/test/folder',
            ('General', 'folders'): '/test/folder',
            ('APIKeys', 'openai_api_key'): 'sk-test',
            ('LocalLLM', 'model_path'): '/models/gpt.gguf',
            ('LocalLLM', 'provider'): 'local'
        }.get((section, key), fallback)
        
        mock_config.getboolean.side_effect = lambda section, key, fallback=False: {
            ('General', 'auto_index'): True
        }.get((section, key), fallback)
        
        mock_load_config.return_value = mock_config
        
        response = self.client.get("/api/config")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['folders'], ['/test/folder'])
        self.assertEqual(data['auto_index'], True)
        self.assertEqual(data['provider'], 'local')

    @patch('api.save_config_file')
    def test_update_config(self, mock_save_config):
        """Test updating configuration."""
        response = self.client.post("/api/config", json={
            "folders": ["/new/folder"],
            "auto_index": False,
            "openai_api_key": "sk-new",
            "local_model_path": "",
            "provider": "openai"
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        mock_save_config.assert_called_once()

    @patch('api.load_config')
    @patch('api.search')
    @patch('api.summarize')
    @patch('llm_integration.smart_summary') # Correct patch path
    @patch('api.get_embeddings')
    def test_search_endpoint(self, mock_get_embeddings, mock_smart_summary, mock_summarize, mock_search, mock_load_config):
        """Test the search endpoint."""
        # Mock config
        mock_config = MagicMock()
        mock_config.get.return_value = 'openai'
        mock_load_config.return_value = mock_config
        
        # Mock index presence (global in api.py)
        with patch('api.index', MagicMock()), \
             patch('api.docs', []), \
             patch('api.tags', []):
            
            # Mock search results
            mock_search.return_value = [{
                'document': 'content',
                'tags': ['tag1']
            }]
            
            # Mock summary
            mock_summarize.return_value = "Summary"
            mock_smart_summary.return_value = "Smart Summary"
            
            response = self.client.post("/api/search", json={
                "query": "test query"
            })
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            # Response is a dict with results, ai_answer, active_model
            self.assertIsInstance(data, dict)
            self.assertIn('results', data)
            self.assertIn('ai_answer', data)
            self.assertIn('active_model', data)
            self.assertEqual(len(data['results']), 1)
            self.assertEqual(data['results'][0]['summary'], "Smart Summary")

    @patch('api.load_config')
    @patch('api.BackgroundTasks.add_task')
    def test_index_endpoint(self, mock_add_task, mock_load_config):
        """Test the index endpoint."""
        mock_config = MagicMock()
        mock_config.get.return_value = '/test/folder'
        mock_load_config.return_value = mock_config
        
        with patch('os.path.exists', return_value=True):
            response = self.client.post("/api/index")
            
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['status'], 'accepted')
            mock_add_task.assert_called_once()

if __name__ == '__main__':
    unittest.main()
