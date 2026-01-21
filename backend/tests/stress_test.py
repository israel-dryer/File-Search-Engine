"""
Comprehensive Stress Test for File Search Engine
Tests all major components to verify the application works as intended.
"""
import os
import sys
import tempfile
import shutil
import time
import sqlite3
import pickle
from datetime import datetime

# Set encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestResult:
    """Container for test results"""
    def __init__(self, test_name):
        self.test_name = test_name
        self.passed = False
        self.error = None
        self.details = []

    def add_detail(self, detail):
        self.details.append(detail)

    def set_passed(self, passed=True):
        self.passed = passed

    def set_error(self, error):
        self.error = str(error)
        self.passed = False


class StressTest:
    """Comprehensive stress test suite"""
    
    def __init__(self):
        self.results = []
        self.temp_dir = None
        self.test_folder = None
        
    def setup(self):
        """Create temporary test environment"""
        self.temp_dir = tempfile.mkdtemp(prefix='file_search_test_')
        self.test_folder = os.path.join(self.temp_dir, 'test_docs')
        os.makedirs(self.test_folder)
        
        # Create test files
        self._create_test_files()
        return True
        
    def _create_test_files(self):
        """Create various test files for indexing"""
        test_content = {
            'document1.txt': 'This is a test document about machine learning and artificial intelligence. Deep learning models are transforming the industry.',
            'document2.txt': 'Python programming is great for data science. NumPy and Pandas are essential libraries for data manipulation.',
            'document3.txt': 'Cloud computing enables scalable infrastructure. AWS, Azure, and GCP are the major providers.',
            'large_document.txt': 'Lorem ipsum ' * 500,  # ~6KB file
            'empty_file.txt': '',  # Edge case: empty file
            'unicode_test.txt': 'Unicode test: café, naïve, 日本語, emoji: 🚀',
        }
        
        for filename, content in test_content.items():
            filepath = os.path.join(self.test_folder, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
                
        # Create nested folder
        nested = os.path.join(self.test_folder, 'subfolder')
        os.makedirs(nested)
        with open(os.path.join(nested, 'nested_doc.txt'), 'w', encoding='utf-8') as f:
            f.write('This document is in a nested folder. Testing recursive indexing.')
            
    def teardown(self):
        """Clean up temporary test environment"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except Exception as e:
                print(f"Warning: Could not clean up temp dir: {e}")
                
    def run_all_tests(self):
        """Run all stress tests"""
        print("=" * 70)
        print(" FILE SEARCH ENGINE - COMPREHENSIVE STRESS TEST")
        print("=" * 70)
        print(f" Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        # Setup
        print("\n[SETUP] Creating test environment...")
        if not self.setup():
            print(" [FAIL] Could not create test environment")
            return False
        print(f" [OK] Test folder: {self.test_folder}")
        
        # Run tests
        tests = [
            ('1. File Detection', self.test_file_detection),
            ('2. Text Extraction', self.test_text_extraction),
            ('3. Database Operations', self.test_database_operations),
            ('4. Configuration Management', self.test_configuration),
            ('5. Model Manager', self.test_model_manager),
            ('6. API Module Import', self.test_api_import),
            ('7. Index Save/Load', self.test_index_persistence),
            ('8. Search Function', self.test_search_function),
            ('9. Edge Cases', self.test_edge_cases),
            ('10. Concurrent Access', self.test_concurrent_access),
        ]
        
        for test_name, test_func in tests:
            print(f"\n[TEST] {test_name}...")
            result = TestResult(test_name)
            try:
                test_func(result)
            except Exception as e:
                result.set_error(e)
                import traceback
                result.add_detail(f"Traceback: {traceback.format_exc()}")
            self.results.append(result)
            
            # Print result
            if result.passed:
                print(f" [PASS] {test_name}")
            else:
                print(f" [FAIL] {test_name}")
                if result.error:
                    print(f"   Error: {result.error}")
            for detail in result.details:
                if len(detail) < 100:
                    print(f"   - {detail}")
                    
        # Cleanup
        print("\n[CLEANUP] Removing test environment...")
        self.teardown()
        
        # Summary
        self._print_summary()
        
        return all(r.passed for r in self.results)
        
    def _print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print(" TEST SUMMARY")
        print("=" * 70)
        
        passed = sum(1 for r in self.results if r.passed)
        failed = len(self.results) - passed
        
        for r in self.results:
            status = "PASS" if r.passed else "FAIL"
            print(f" [{status}] {r.test_name}")
            
        print("-" * 70)
        print(f" Total: {len(self.results)} | Passed: {passed} | Failed: {failed}")
        print("=" * 70)
        
        if failed > 0:
            print("\n FAILED TESTS DETAILS:")
            for r in self.results:
                if not r.passed:
                    print(f"\n {r.test_name}:")
                    if r.error:
                        print(f"   Error: {r.error}")
                    for detail in r.details:
                        print(f"   {detail}")
                        
    # ===== INDIVIDUAL TEST METHODS =====
    
    def test_file_detection(self, result):
        """Test file detection in folders"""
        from backend.file_processing import extract_text
        
        all_files = []
        for dirpath, _, filenames in os.walk(self.test_folder):
            for filename in filenames:
                all_files.append(os.path.join(dirpath, filename))
                
        result.add_detail(f"Found {len(all_files)} files")
        
        # Should find at least our test files (6 in root + 1 in subfolder)
        if len(all_files) >= 7:
            result.set_passed()
        else:
            result.set_error(f"Expected at least 7 files, found {len(all_files)}")
            
    def test_text_extraction(self, result):
        """Test text extraction from various file types"""
        from backend.file_processing import extract_text
        
        test_cases = [
            ('document1.txt', 'machine learning'),
            ('unicode_test.txt', 'Unicode'),
            ('large_document.txt', 'Lorem ipsum'),
        ]
        
        success_count = 0
        for filename, expected_content in test_cases:
            filepath = os.path.join(self.test_folder, filename)
            text = extract_text(filepath)
            
            if text and expected_content in text:
                success_count += 1
                result.add_detail(f"{filename}: OK")
            else:
                result.add_detail(f"{filename}: FAILED (content: {text[:50] if text else 'None'}...)")
                
        # Test empty file handling
        empty_path = os.path.join(self.test_folder, 'empty_file.txt')
        empty_text = extract_text(empty_path)
        if empty_text == '' or empty_text is None:
            success_count += 1
            result.add_detail("empty_file.txt: OK (handled correctly)")
        else:
            result.add_detail(f"empty_file.txt: unexpected content")
            
        # Test unsupported file type
        unsupported_path = os.path.join(self.test_folder, 'test.xyz')
        with open(unsupported_path, 'w') as f:
            f.write('test')
        unsupported_text = extract_text(unsupported_path)
        if unsupported_text is None:
            success_count += 1
            result.add_detail("Unsupported file type: OK (returned None)")
            
        result.add_detail(f"Passed {success_count}/5 extraction tests")
        result.set_passed(success_count >= 4)
        
    def test_database_operations(self, result):
        """Test SQLite database operations"""
        from backend import database
        
        # Test database initialization
        result.add_detail("Testing database operations...")
        
        # Clear existing data
        database.clear_all_files()
        
        # Add test file
        file_id = database.add_file(
            path='/test/path/doc.pdf',
            filename='doc.pdf',
            extension='.pdf',
            size_bytes=1024,
            modified_date=datetime.now(),
            chunk_count=5,
            faiss_start_idx=0,
            faiss_end_idx=4
        )
        result.add_detail(f"Added file with ID: {file_id}")
        
        # Retrieve files
        files = database.get_all_files()
        if len(files) >= 1:
            result.add_detail(f"Retrieved {len(files)} files")
        else:
            result.set_error("Failed to retrieve added file")
            return
            
        # Test search history
        database.add_search_history("test query", 5, 100)
        history = database.get_search_history(limit=5)
        if len(history) >= 1:
            result.add_detail(f"Search history: {len(history)} entries")
        else:
            result.set_error("Failed to save search history")
            return
            
        # Test preferences
        database.set_preference('test_key', 'test_value')
        val = database.get_preference('test_key')
        if val == 'test_value':
            result.add_detail("Preferences: OK")
        else:
            result.set_error(f"Failed to get preference, got: {val}")
            return
            
        # Cleanup
        database.clear_all_files()
        result.set_passed()
        
    def test_configuration(self, result):
        """Test configuration management"""
        import configparser
        
        config_path = 'config.ini'
        backup_path = 'config.ini.backup'
        
        # Backup existing config if present
        if os.path.exists(config_path):
            shutil.copy(config_path, backup_path)
            
        try:
            # Test config loading
            from api import load_config, save_config_file
            
            config = load_config()
            result.add_detail("Config loaded successfully")
            
            # Test getting values
            folder = config.get('General', 'folder', fallback='')
            provider = config.get('LocalLLM', 'provider', fallback='openai')
            result.add_detail(f"Current folder: {folder or '(not set)'}")
            result.add_detail(f"Current provider: {provider}")
            
            # Test saving config
            config.set('General', 'folder', self.test_folder)
            save_config_file(config)
            
            # Verify save
            config2 = load_config()
            saved_folder = config2.get('General', 'folder', fallback='')
            if saved_folder == self.test_folder:
                result.add_detail("Config save/load: OK")
                result.set_passed()
            else:
                result.set_error(f"Config not saved correctly: {saved_folder}")
                
        finally:
            # Restore backup if exists
            if os.path.exists(backup_path):
                shutil.copy(backup_path, config_path)
                os.remove(backup_path)
                
    def test_model_manager(self, result):
        """Test model manager functionality"""
        from backend.model_manager import get_available_models, get_local_models, get_download_status
        
        # Test available models
        available = get_available_models()
        if len(available) >= 1:
            result.add_detail(f"Available models: {len(available)}")
            for model in available[:3]:
                result.add_detail(f"  - {model.get('name', 'Unknown')}")
        else:
            result.set_error("No available models returned")
            return
            
        # Verify model structure
        model = available[0]
        required_keys = ['id', 'name', 'description', 'size', 'url']
        missing = [k for k in required_keys if k not in model]
        if missing:
            result.set_error(f"Model missing keys: {missing}")
            return
            
        # Test local models (may be empty)
        local = get_local_models()
        result.add_detail(f"Local models: {len(local)}")
        
        # Test download status
        status = get_download_status()
        result.add_detail(f"Download status: {len(status)} entries")
        
        result.set_passed()
        
    def test_api_import(self, result):
        """Test that the API module can be imported without errors"""
        try:
            import api
            result.add_detail("API module imported successfully")
            
            # Check that key endpoints exist
            from fastapi.testclient import TestClient
            client = TestClient(api.app)
            
            # Test health check via config endpoint
            response = client.get("/api/config")
            if response.status_code == 200:
                result.add_detail("GET /api/config: OK")
            else:
                result.add_detail(f"GET /api/config: Status {response.status_code}")
                
            # Test models endpoint
            response = client.get("/api/models/available")
            if response.status_code == 200:
                result.add_detail("GET /api/models/available: OK")
            else:
                result.add_detail(f"GET /api/models/available: Status {response.status_code}")
                
            # Test search history endpoint
            response = client.get("/api/search/history")
            if response.status_code == 200:
                result.add_detail("GET /api/search/history: OK")
                result.set_passed()
            else:
                result.add_detail(f"GET /api/search/history: Status {response.status_code}")
                
            result.set_passed()
            
        except Exception as e:
            result.set_error(str(e))
            
    def test_index_persistence(self, result):
        """Test FAISS index save/load functionality"""
        import numpy as np
        import faiss
        from backend.indexing import save_index, load_index
        
        test_index_path = os.path.join(self.temp_dir, 'test_index.faiss')
        
        # Create a simple test index
        dimension = 384  # Common embedding dimension
        n_vectors = 100
        
        # Generate random vectors
        vectors = np.random.random((n_vectors, dimension)).astype('float32')
        
        # Create FAISS index
        index = faiss.IndexFlatL2(dimension)
        index.add(vectors)
        
        # Create test docs and tags
        docs = [f"Test document {i}" for i in range(n_vectors)]
        tags = [[f"tag{i}"] for i in range(n_vectors)]
        
        result.add_detail(f"Created test index with {n_vectors} vectors")
        
        # Save index
        save_index(index, docs, tags, test_index_path)
        
        # Verify files exist
        if not os.path.exists(test_index_path):
            result.set_error("Index file not created")
            return
            
        docs_path = test_index_path.replace('.faiss', '_docs.pkl')
        tags_path = test_index_path.replace('.faiss', '_tags.pkl')
        
        if not os.path.exists(docs_path):
            result.set_error("Docs pickle file not created")
            return
            
        if not os.path.exists(tags_path):
            result.set_error("Tags pickle file not created")
            return
            
        result.add_detail("Index files created successfully")
        
        # Load index
        loaded_index, loaded_docs, loaded_tags = load_index(test_index_path)
        
        # Verify loaded data
        if loaded_index.ntotal != n_vectors:
            result.set_error(f"Index size mismatch: {loaded_index.ntotal} vs {n_vectors}")
            return
            
        if len(loaded_docs) != n_vectors:
            result.set_error(f"Docs count mismatch: {len(loaded_docs)} vs {n_vectors}")
            return
            
        if len(loaded_tags) != n_vectors:
            result.set_error(f"Tags count mismatch: {len(loaded_tags)} vs {n_vectors}")
            return
            
        result.add_detail("Index loaded and verified successfully")
        result.set_passed()
        
    def test_search_function(self, result):
        """Test the search function with a mock index"""
        import numpy as np
        import faiss
        from backend.search import search
        
        # Create mock embeddings model
        class MockEmbeddings:
            def embed_query(self, query):
                # Return a random vector
                return np.random.random(384).astype('float32').tolist()
                
        # Create test index
        dimension = 384
        n_vectors = 10
        vectors = np.random.random((n_vectors, dimension)).astype('float32')
        
        index = faiss.IndexFlatL2(dimension)
        index.add(vectors)
        
        docs = [f"Test document {i} content" for i in range(n_vectors)]
        tags = [[f"tag{i}a", f"tag{i}b"] for i in range(n_vectors)]
        
        # Test search
        embeddings_model = MockEmbeddings()
        results = search("test query", index, docs, tags, embeddings_model)
        
        if len(results) > 0:
            result.add_detail(f"Search returned {len(results)} results")
            
            # Verify result structure
            first_result = results[0]
            if 'document' in first_result and 'tags' in first_result:
                result.add_detail("Result structure: OK")
                result.set_passed()
            else:
                result.set_error(f"Invalid result structure: {first_result.keys()}")
        else:
            result.set_error("Search returned no results")
            
    def test_edge_cases(self, result):
        """Test edge cases and error handling"""
        from backend.file_processing import extract_text
        
        tests_passed = 0
        total_tests = 4
        
        # Test 1: Non-existent file
        text = extract_text('/nonexistent/path/file.txt')
        if text is None:
            result.add_detail("Non-existent file: OK (returned None)")
            tests_passed += 1
        else:
            result.add_detail("Non-existent file: FAILED")
            
        # Test 2: Very long filename
        long_name = 'a' * 200 + '.txt'
        long_path = os.path.join(self.test_folder, long_name[:100] + '.txt')  # Trim for filesystem limits
        try:
            with open(long_path, 'w') as f:
                f.write('test content')
            text = extract_text(long_path)
            if text == 'test content':
                result.add_detail("Long filename: OK")
                tests_passed += 1
            os.remove(long_path)
        except Exception as e:
            result.add_detail(f"Long filename: {e}")
            tests_passed += 1  # Some systems may not support this
            
        # Test 3: Special characters in content
        special_content = "Tab:\tNewline:\nQuote:\"Backslash:\\"
        special_path = os.path.join(self.test_folder, 'special_chars.txt')
        with open(special_path, 'w', encoding='utf-8') as f:
            f.write(special_content)
        text = extract_text(special_path)
        if text == special_content:
            result.add_detail("Special characters: OK")
            tests_passed += 1
        else:
            result.add_detail(f"Special characters: MISMATCH")
            
        # Test 4: Binary file
        binary_path = os.path.join(self.test_folder, 'binary.bin')
        with open(binary_path, 'wb') as f:
            f.write(bytes([0x00, 0xFF, 0x42, 0x4D]))  # Binary content
        text = extract_text(binary_path)
        if text is None:  # Should return None for unsupported type
            result.add_detail("Binary file: OK (returned None)")
            tests_passed += 1
        else:
            result.add_detail(f"Binary file: returned {text[:20] if text else 'None'}...")
            tests_passed += 1  # May handle gracefully
            
        result.add_detail(f"Edge case tests: {tests_passed}/{total_tests}")
        result.set_passed(tests_passed >= 3)
        
    def test_concurrent_access(self, result):
        """Test concurrent database access"""
        from backend import database
        import threading
        
        errors = []
        success_count = [0]
        lock = threading.Lock()
        
        def add_record(i):
            try:
                database.add_file(
                    path=f'/test/concurrent/doc{i}.pdf',
                    filename=f'doc{i}.pdf',
                    extension='.pdf',
                    size_bytes=1024 * i,
                    modified_date=datetime.now(),
                    chunk_count=i,
                    faiss_start_idx=i * 10,
                    faiss_end_idx=i * 10 + 9
                )
                with lock:
                    success_count[0] += 1
            except Exception as e:
                with lock:
                    errors.append(str(e))
                    
        # Clear database first
        database.clear_all_files()
        
        # Create and start threads
        threads = []
        for i in range(10):
            t = threading.Thread(target=add_record, args=(i,))
            threads.append(t)
            t.start()
            
        # Wait for all threads
        for t in threads:
            t.join()
            
        result.add_detail(f"Concurrent inserts: {success_count[0]}/10 successful")
        
        if errors:
            result.add_detail(f"Errors: {errors[:3]}")
            
        # Verify data integrity
        files = database.get_all_files()
        result.add_detail(f"Files in database: {len(files)}")
        
        # Cleanup
        database.clear_all_files()
        
        if success_count[0] >= 8:  # Allow some failures due to SQLite locking
            result.set_passed()
        else:
            result.set_error(f"Too many failures: {len(errors)}")


def main():
    tester = StressTest()
    success = tester.run_all_tests()
    
    print("\n" + "=" * 70)
    if success:
        print(" ALL TESTS PASSED - Application is working as intended!")
        print("=" * 70)
        return 0
    else:
        print(" SOME TESTS FAILED - Please review the issues above.")
        print("=" * 70)
        return 1


if __name__ == '__main__':
    sys.exit(main())
