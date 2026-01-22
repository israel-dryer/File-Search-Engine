"""
Test Database Module

Tests for the database module including file tracking,
search history, and metadata storage.
"""

import unittest
import os
import tempfile
import shutil


# Shared temp database setup for ALL test classes
_shared_temp_dir = None
_original_db_path = None


def setUpModule():
    """Set up shared temp database for all tests in this module."""
    global _shared_temp_dir, _original_db_path
    from backend import database
    
    # Create shared temp directory
    _shared_temp_dir = tempfile.mkdtemp()
    _original_db_path = database.DATABASE_PATH
    database.DATABASE_PATH = os.path.join(_shared_temp_dir, 'test_metadata.db')
    database.init_database()


def tearDownModule():
    """Clean up shared temp database."""
    global _shared_temp_dir, _original_db_path
    from backend import database
    import gc
    import time
    
    # Restore original path
    database.DATABASE_PATH = _original_db_path
    
    # Try to close any lingering connections and clean up
    gc.collect()
    time.sleep(0.1)  # Small delay to let OS release file handles
    
    if _shared_temp_dir and os.path.exists(_shared_temp_dir):
        try:
            shutil.rmtree(_shared_temp_dir)
        except Exception as e:
            print(f"Warning: Could not clean up test directory {_shared_temp_dir}: {e}")


class TestDatabase(unittest.TestCase):
    """Tests for database module."""
    
    # No need for setUpClass/tearDownClass - using module-level setup
    
    def test_folder_history(self):
        """Test folder history operations."""
        from backend import database
        
        # Add folder
        database.add_folder_to_history('/test/hist1')
        
        # Get history
        hist = database.get_folder_history()
        self.assertTrue(any(h['path'] == '/test/hist1' for h in hist))
        
        # Add another
        database.add_folder_to_history('/test/hist2')
        hist2 = database.get_folder_history()
        self.assertEqual(hist2[0]['path'], '/test/hist2')
    
    def test_delete_folder_history_item(self):
        """Test deleting a single folder from history."""
        from backend import database
        
        # Add a test folder
        test_path = '/test/delete_single'
        database.add_folder_to_history(test_path)
        
        # Verify it exists
        hist = database.get_folder_history()
        self.assertTrue(any(h['path'] == test_path for h in hist))
        
        # Delete it
        result = database.delete_folder_history_item(test_path)
        self.assertTrue(result)
        
        # Verify it's gone
        hist_after = database.get_folder_history()
        self.assertFalse(any(h['path'] == test_path for h in hist_after))
    
    def test_delete_nonexistent_folder_history_item(self):
        """Test deleting a folder that doesn't exist in history."""
        from backend import database
        
        result = database.delete_folder_history_item('/nonexistent/path/12345')
        self.assertFalse(result)
    
    def test_clear_folder_history(self):
        """Test clearing all folder history."""
        from backend import database
        
        # Add some folders
        database.add_folder_to_history('/test/clear1')
        database.add_folder_to_history('/test/clear2')
        
        # Clear all
        count = database.clear_folder_history()
        self.assertIsInstance(count, int)
        
        # Verify empty
        hist = database.get_folder_history()
        self.assertEqual(len(hist), 0)

    def test_database_initialization(self):
        """Test that database is properly initialized."""
        from backend import database
        
        # Should not raise
        database.init_database()
        
        # Check that get_connection exists
        self.assertTrue(
            hasattr(database, 'get_connection'),
            "Database should have get_connection function"
        )
    
    def test_add_file_metadata(self):
        """Test adding file metadata to database."""
        from backend import database
        from datetime import datetime
        
        # Should not raise
        try:
            database.add_file(
                path='/test/path/document.pdf',
                filename='document.pdf',
                extension='.pdf',
                size_bytes=1024,
                modified_date=datetime.now(),
                chunk_count=1,
                faiss_start_idx=0,
                faiss_end_idx=0
            )
        except Exception as e:
            self.fail(f"Failed to add file: {e}")
    
    def test_get_file_by_faiss_index(self):
        """Test retrieving file by FAISS index."""
        from backend import database
        from datetime import datetime
        
        # First add a file
        test_path = '/test/retrieval/test.txt'
        database.add_file(
            path=test_path,
            filename='test.txt',
            extension='.txt',
            size_bytes=512,
            modified_date=datetime.now(),
            chunk_count=1,
            faiss_start_idx=999,
            faiss_end_idx=999
        )
        
        # Try to retrieve it
        file_info = database.get_file_by_faiss_index(999)
        
        if file_info:
            self.assertEqual(file_info['path'], test_path)
            self.assertEqual(file_info['filename'], 'test.txt')
    
    def test_add_search_history(self):
        """Test adding search history entries."""
        from backend import database
        
        # Should not raise - using correct parameter names
        try:
            database.add_search_history(
                query="test query",
                result_count=5,
                execution_time_ms=100
            )
        except Exception as e:
            self.fail(f"Failed to add search history: {e}")
    
    def test_get_search_history(self):
        """Test retrieving search history."""
        from backend import database
        
        # Add a search entry
        database.add_search_history("history test query", 3, 50)
        
        # Get history
        history = database.get_search_history(limit=10)
        self.assertIsInstance(history, list)
    
    def test_get_all_files(self):
        """Test getting all indexed files."""
        from backend import database
        
        files = database.get_all_files()
        self.assertIsInstance(files, list)
    
    def test_clear_files(self):
        """Test clearing all file entries."""
        from backend import database
        
        # Should not raise
        try:
            database.clear_all_files()
        except Exception as e:
            self.fail(f"Failed to clear files: {e}")


class TestDatabaseSearchHistory(unittest.TestCase):
    """Tests specifically for search history functionality."""
    
    def test_history_structure(self):
        """Test that search history entries have correct structure."""
        from backend import database
        
        # Add an entry
        database.add_search_history("structure test", 2, 30)
        
        history = database.get_search_history(limit=1)
        
        if history:
            entry = history[0]
            self.assertIn('query', entry)
            self.assertIn('result_count', entry)
            self.assertIn('execution_time_ms', entry)
    
    def test_delete_search_history(self):
        """Test deleting search history."""
        from backend import database
        
        if hasattr(database, 'delete_all_search_history'):
            deleted_count = database.delete_all_search_history()
            self.assertIsInstance(deleted_count, int)
    
    def test_delete_single_history_item(self):
        """Test deleting a single search history item."""
        from backend import database
        
        # Add a search entry
        database.add_search_history("delete single test", 1, 10)
        
        # Get the most recent entry
        history = database.get_search_history(limit=1)
        if history:
            history_id = history[0]['id']
            result = database.delete_search_history_item(history_id)
            self.assertTrue(result)
    
    def test_delete_nonexistent_history_item(self):
        """Test deleting a history item that doesn't exist."""
        from backend import database
        
        # Try to delete a non-existent ID
        result = database.delete_search_history_item(999999)
        self.assertFalse(result)


class TestDatabaseFileOperations(unittest.TestCase):
    """Tests for file CRUD operations."""
    
    # Using module-level database setup
    
    def test_get_file_by_path_existing(self):
        """Test retrieving a file by path that exists."""
        from backend import database
        from datetime import datetime
        
        test_path = '/test/get_by_path/existing.pdf'
        database.add_file(
            path=test_path,
            filename='existing.pdf',
            extension='.pdf',
            size_bytes=2048,
            modified_date=datetime.now(),
            chunk_count=2,
            faiss_start_idx=100,
            faiss_end_idx=101
        )
        
        file_info = database.get_file_by_path(test_path)
        
        self.assertIsNotNone(file_info)
        self.assertEqual(file_info['path'], test_path)
        self.assertEqual(file_info['filename'], 'existing.pdf')
        self.assertEqual(file_info['size_bytes'], 2048)
    
    def test_get_file_by_path_nonexistent(self):
        """Test retrieving a file by path that doesn't exist."""
        from backend import database
        
        file_info = database.get_file_by_path('/nonexistent/path/file.txt')
        self.assertIsNone(file_info)
    
    def test_delete_file(self):
        """Test deleting a file from the database."""
        from backend import database
        from datetime import datetime
        
        test_path = '/test/delete/todelete.pdf'
        file_id = database.add_file(
            path=test_path,
            filename='todelete.pdf',
            extension='.pdf',
            size_bytes=512,
            modified_date=datetime.now(),
            chunk_count=1,
            faiss_start_idx=200,
            faiss_end_idx=200
        )
        
        # Verify file exists
        file_info = database.get_file_by_path(test_path)
        self.assertIsNotNone(file_info)
        
        # Delete the file
        database.delete_file(file_info['id'])
        
        # Verify file is gone
        file_info_after = database.get_file_by_path(test_path)
        self.assertIsNone(file_info_after)
    
    def test_get_file_by_faiss_index_not_found(self):
        """Test retrieving file by FAISS index that doesn't exist."""
        from backend import database
        
        file_info = database.get_file_by_faiss_index(888888)
        self.assertIsNone(file_info)


class TestDatabasePreferences(unittest.TestCase):
    """Tests for preferences storage."""
    
    # Using module-level database setup
    
    def test_set_and_get_preference(self):
        """Test setting and getting a preference."""
        from backend import database
        
        database.set_preference('test_key', 'test_value')
        value = database.get_preference('test_key')
        
        self.assertEqual(value, 'test_value')
    
    def test_get_nonexistent_preference(self):
        """Test getting a preference that doesn't exist."""
        from backend import database
        
        value = database.get_preference('nonexistent_key_12345')
        self.assertIsNone(value)
    
    def test_update_preference(self):
        """Test updating an existing preference."""
        from backend import database
        
        database.set_preference('update_key', 'original_value')
        database.set_preference('update_key', 'updated_value')
        
        value = database.get_preference('update_key')
        self.assertEqual(value, 'updated_value')
    
    def test_preference_with_special_characters(self):
        """Test preferences with special characters."""
        from backend import database
        
        special_value = "path/with/slashes and spaces & symbols!"
        database.set_preference('special_key', special_value)
        
        value = database.get_preference('special_key')
        self.assertEqual(value, special_value)


class TestDatabaseConnection(unittest.TestCase):
    """Tests for database connection handling."""
    
    def test_get_connection_returns_valid_connection(self):
        """Test that get_connection returns a valid SQLite connection."""
        from backend import database
        
        conn = database.get_connection()
        self.assertIsNotNone(conn)
        
        # Test that we can execute a query
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        self.assertEqual(result[0], 1)
        
        conn.close()
    
    def test_multiple_connections(self):
        """Test that multiple connections work correctly."""
        from backend import database
        
        conn1 = database.get_connection()
        conn2 = database.get_connection()
        
        self.assertIsNotNone(conn1)
        self.assertIsNotNone(conn2)
        
        conn1.close()
        conn2.close()


if __name__ == '__main__':
    unittest.main(verbosity=2)
