import unittest
import os
import tempfile
from fastapi.testclient import TestClient
from backend.api import app
from unittest.mock import patch
from backend import model_manager

class TestSecurityApi(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        # Create a temporary file OUTSIDE the models directory
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.close()
        self.temp_path = self.temp_file.name

    def tearDown(self):
        # Clean up if the test didn't delete it
        if os.path.exists(self.temp_path):
            os.remove(self.temp_path)

    def test_arbitrary_file_deletion_prevention(self):
        """
        Verify that deleting a file OUTSIDE the models directory fails.
        """
        print(f"Attempting to delete: {self.temp_path}")

        response = self.client.request(
            "DELETE",
            "/api/models/delete",
            json={"path": self.temp_path}
        )

        # Check if the file still exists
        file_exists = os.path.exists(self.temp_path)

        if file_exists:
            print("SUCCESS: Arbitrary file deletion was blocked.")
        else:
            print("FAILURE: Arbitrary file was deleted.")

        # In our implementation, delete_model returns False if unsafe,
        # causing 404 "Model file not found"
        self.assertEqual(response.status_code, 404, "Should return 404 for unsafe path")
        self.assertTrue(file_exists, "File should NOT be deleted")

    @patch('backend.database.get_file_by_path')
    def test_open_file_security(self, mock_get_file):
        """
        Verify that opening a non-indexed file is forbidden.
        """
        # 1. Try to open a file NOT in database
        mock_get_file.return_value = None

        response = self.client.post("/api/open-file", json={"path": self.temp_path})

        self.assertEqual(response.status_code, 403, "Should deny access to non-indexed file")
        self.assertIn("Access denied", response.json()['detail'])

        # 2. Try to open a file IN database
        mock_get_file.return_value = {'path': self.temp_path}

        # We need to mock os.startfile or subprocess to avoid actually opening it
        # os.startfile is Windows only, subprocess.run is for Mac/Linux
        with patch('os.startfile', create=True) as mock_startfile, \
             patch('subprocess.run') as mock_run:
                 response = self.client.post("/api/open-file", json={"path": self.temp_path})
                 self.assertEqual(response.status_code, 200, "Should allow indexed file")

class TestSecurityUnit(unittest.TestCase):
    """Security regression tests."""

    def test_delete_model_arbitrary_file(self):
        """Test that delete_model prevents deleting files outside models directory."""
        # Create a temporary file outside of MODELS_DIR
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"secret data")
            tmp_path = tmp.name

        try:
            # Ensure the file exists
            self.assertTrue(os.path.exists(tmp_path))

            # Attempt to delete it via model_manager
            # This should fail (return False) and NOT delete the file
            result = model_manager.delete_model(tmp_path)

            # Assertion: Should fail
            self.assertFalse(result, "delete_model should return False for arbitrary paths")

            # Assertion: File should still exist
            self.assertTrue(os.path.exists(tmp_path), "Arbitrary file was deleted!")

        finally:
            # Cleanup
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_delete_model_valid_file(self):
        """Test that delete_model allows deleting files INSIDE models directory."""
        # Ensure models dir exists
        os.makedirs(model_manager.MODELS_DIR, exist_ok=True)

        # Create a dummy model file inside MODELS_DIR
        safe_path = os.path.join(model_manager.MODELS_DIR, "test_safe_model.gguf")
        with open(safe_path, 'wb') as f:
            f.write(b"dummy model content")

        try:
            self.assertTrue(os.path.exists(safe_path))

            # Attempt delete
            result = model_manager.delete_model(safe_path)

            self.assertTrue(result, "Should allow deleting valid model file")
            self.assertFalse(os.path.exists(safe_path), "Valid file should be deleted")

        finally:
            if os.path.exists(safe_path):
                os.remove(safe_path)

if __name__ == '__main__':
    unittest.main()
