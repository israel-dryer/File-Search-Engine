import unittest
import os
import tempfile
from backend import model_manager

class TestSecurity(unittest.TestCase):
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
