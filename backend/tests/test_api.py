"""
Test API Module

Comprehensive tests for all API endpoints including configuration,
search, models, benchmarks, history, and file operations.
"""

import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from backend.api import app

# We will use class-level or method-level patches instead of global ones to avoid inter-test pollution


class TestAPIConfig(unittest.TestCase):
    """Test cases for configuration endpoints."""

    def setUp(self):
        """Set up test client before each test method."""
        self.client = TestClient(app)
    
    @patch('backend.api.load_config')
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

    @patch('backend.database.add_folder_to_history')
    @patch('backend.api.save_config_file')
    def test_update_config(self, mock_save_config, mock_add_history):
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


class TestAPISearch(unittest.TestCase):
    """Test cases for search endpoints."""

    def setUp(self):
        """Set up test client before each test method."""
        self.client = TestClient(app)

    @patch('backend.database.add_search_history')
    @patch('backend.database.get_file_by_faiss_index')
    @patch('backend.llm_integration.cached_generate_ai_answer')
    @patch('backend.llm_integration.cached_smart_summary')
    @patch('backend.api.load_config')
    @patch('backend.api.search')
    @patch('backend.api.summarize')
    @patch('backend.api.get_embeddings')
    def test_search_endpoint(self, mock_get_embeddings, mock_summarize, mock_search, mock_load_config, 
                              mock_smart_summary, mock_generate_ai, mock_get_file, mock_add_history):
        """Test the search endpoint."""
        mock_config = MagicMock()
        mock_config.get.return_value = 'openai'
        mock_load_config.return_value = mock_config
        
        mock_get_file.return_value = {'filename': 'test.pdf', 'path': '/test/test.pdf'}
        mock_smart_summary.return_value = "Smart Summary"
        mock_generate_ai.return_value = "AI Answer"
        
        with patch('backend.api.index', MagicMock()), \
             patch('backend.api.docs', []), \
             patch('backend.api.tags', []):
            
            mock_search.return_value = (
                [{'document': 'content', 'tags': ['tag1'], 'faiss_idx': 0}],
                ['context snippet']
            )
            
            mock_summarize.return_value = "Summary"
            mock_smart_summary.return_value = "Smart Summary"
            mock_generate_ai.return_value = "AI Answer"
            
            response = self.client.post("/api/search", json={
                "query": "test query"
            })
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIsInstance(data, dict)
            self.assertIn('results', data)
            self.assertIn('ai_answer', data)
            self.assertIn('active_model', data)


    def test_search_without_index(self):
        """Test search when no index is loaded."""
        with patch('backend.api.index', None):
            response = self.client.post("/api/search", json={
                "query": "test query"
            })
            self.assertEqual(response.status_code, 400)


class TestAPIModels(unittest.TestCase):
    """Test cases for model management endpoints."""

    def setUp(self):
        """Set up test client before each test method."""
        self.client = TestClient(app)

    @patch('backend.api.get_available_models')
    def test_list_available_models(self, mock_get_available):
        """Test listing available models."""
        mock_get_available.return_value = [
            {'id': 'model1', 'name': 'Model 1', 'size': '1GB'},
            {'id': 'model2', 'name': 'Model 2', 'size': '2GB'}
        ]
        
        response = self.client.get("/api/models/available")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)

    @patch('backend.api.get_local_models')
    def test_list_local_models(self, mock_get_local):
        """Test listing local downloaded models."""
        mock_get_local.return_value = [
            {'id': 'local1', 'path': '/models/local1.gguf', 'size': 1000000}
        ]
        
        response = self.client.get("/api/models/local")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)

    @patch('backend.api.start_download')
    def test_download_model_endpoint(self, mock_start_download):
        """Test starting model download."""
        mock_start_download.return_value = (True, "Download started")
        
        response = self.client.post("/api/models/download/test-model")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('status', data)

    @patch('backend.api.get_download_status')
    def test_download_status_endpoint(self, mock_get_status):
        """Test getting download status."""
        mock_get_status.return_value = {
            'downloading': True,
            'model_id': 'test-model',
            'progress': 50
        }
        
        response = self.client.get("/api/models/status")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('downloading', data)
        self.assertIn('progress', data)

    @patch('backend.model_manager.delete_model')
    def test_delete_model(self, mock_delete):
        """Test deleting a model."""
        mock_delete.return_value = True
        
        # Use request method as workaround for delete which doesn't support json in some TestClient versions
        response = self.client.request(
            "DELETE", 
            "/api/models/delete", 
            json={"path": "/models/test.gguf"}
        )
        
        self.assertEqual(response.status_code, 200)


class TestAPIBenchmarks(unittest.TestCase):
    """Test cases for benchmark endpoints."""

    def setUp(self):
        """Set up test client before each test method."""
        self.client = TestClient(app)

    def test_get_benchmark_status(self):
        """Test getting benchmark status."""
        response = self.client.get("/api/benchmarks/status")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('running', data)

    @patch('backend.api.benchmark_results', {'test': 'results'})
    def test_get_benchmark_results_with_data(self):
        """Test getting benchmark results when available."""
        with patch('backend.api.benchmark_results', {'model': 'test', 'score': 100}):
            response = self.client.get("/api/benchmarks/results")
            self.assertEqual(response.status_code, 200)

    @patch('backend.api.BackgroundTasks.add_task')
    @patch('backend.api.benchmark_status', {'running': False})
    def test_run_benchmarks_endpoint(self, mock_add_task):
        """Test starting benchmarks."""
        response = self.client.post("/api/benchmarks/run")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'started')
        mock_add_task.assert_called_once()


class TestAPISearchHistory(unittest.TestCase):
    """Test cases for search history endpoints."""

    def setUp(self):
        """Set up test client before each test method."""
        self.client = TestClient(app)

    @patch('backend.database.get_search_history')
    def test_get_search_history(self, mock_get_history):
        """Test getting search history."""
        mock_get_history.return_value = [
            {'id': 1, 'query': 'test', 'timestamp': '2024-01-01', 'result_count': 5}
        ]
        
        response = self.client.get("/api/search/history")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)

    @patch('backend.database.delete_search_history_item')
    def test_delete_search_history_item(self, mock_delete):
        """Test deleting a single history item."""
        mock_delete.return_value = True
        
        response = self.client.delete("/api/search/history/1")
        
        self.assertEqual(response.status_code, 200)

    @patch('backend.database.delete_all_search_history')
    def test_delete_all_search_history(self, mock_delete_all):
        """Test deleting all search history."""
        mock_delete_all.return_value = 5
        
        response = self.client.delete("/api/search/history")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('deleted_count', data)


class TestAPIFileOperations(unittest.TestCase):
    """Test cases for file operation endpoints."""

    def setUp(self):
        """Set up test client before each test method."""
        self.client = TestClient(app)

    @patch('backend.database.get_all_files')
    def test_list_indexed_files(self, mock_get_files):
        """Test listing indexed files."""
        mock_get_files.return_value = [
            {'id': 1, 'filename': 'test.pdf', 'path': '/test.pdf', 'size_bytes': 1024}
        ]
        
        response = self.client.get("/api/files")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)

    def test_validate_path_valid(self):
        """Test validating a valid path."""
        with patch('os.path.exists', return_value=True), \
             patch('os.path.isdir', return_value=True), \
             patch('os.walk', return_value=[('/test', [], ['file1.pdf', 'file2.docx'])]):
            response = self.client.post("/api/validate-path", json={
                "path": "/test/folder"
            })
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertTrue(data['valid'])

    def test_validate_path_invalid(self):
        """Test validating an invalid path."""
        with patch('os.path.exists', return_value=False):
            response = self.client.post("/api/validate-path", json={
                "path": "/nonexistent/folder"
            })
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertFalse(data['valid'])

    @patch('backend.database.get_file_by_path')
    @patch('os.startfile', create=True)
    def test_open_file(self, mock_startfile, mock_get_file):
        """Test opening a file."""
        mock_get_file.return_value = {'path': '/test/document.pdf'}
        with patch('os.path.exists', return_value=True):
            response = self.client.post("/api/open-file", json={
                "path": "/test/document.pdf"
            })
            
            self.assertEqual(response.status_code, 200)


class TestAPIIndexing(unittest.TestCase):
    """Test cases for indexing endpoints."""

    def setUp(self):
        """Set up test client before each test method."""
        self.client = TestClient(app)

    @patch('backend.api.load_config')
    @patch('backend.api.BackgroundTasks.add_task')
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

    def test_get_indexing_status(self):
        """Test getting indexing status."""
        response = self.client.get("/api/index/status")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('running', data)


if __name__ == '__main__':
    unittest.main()
