import unittest
import sys
import os
from unittest.mock import MagicMock

# Mock dependencies if they are missing
if 'requests' not in sys.modules:
    sys.modules['requests'] = MagicMock()
if 'psutil' not in sys.modules:
    sys.modules['psutil'] = MagicMock()

# Ensure backend can be imported
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from backend.model_manager import delete_model, MODELS_DIR

class TestModelManagerSecurity(unittest.TestCase):
    """Security tests for model manager."""

    def test_delete_model_path_traversal(self):
        """Test that delete_model prevents path traversal."""
        # Create a dummy file outside MODELS_DIR
        vulnerable_file = os.path.abspath("vulnerable_test_file.txt")
        with open(vulnerable_file, "w") as f:
            f.write("sensitive data")

        try:
            # Attempt to delete
            result = delete_model(vulnerable_file)

            # Should fail (return False) and file should still exist
            self.assertFalse(result, "delete_model should return False for unsafe path")
            self.assertTrue(os.path.exists(vulnerable_file), "Vulnerable file should not be deleted")

        finally:
            # Cleanup
            if os.path.exists(vulnerable_file):
                os.remove(vulnerable_file)

    def test_delete_model_valid(self):
        """Test that delete_model works for valid files."""
        # Ensure models dir exists
        os.makedirs(MODELS_DIR, exist_ok=True)

        # Create a dummy file inside MODELS_DIR
        valid_file = os.path.join(MODELS_DIR, "valid_test_model.gguf")
        with open(valid_file, "w") as f:
            f.write("dummy model data")

        try:
            # Attempt to delete
            result = delete_model(valid_file)

            # Should succeed
            self.assertTrue(result, "delete_model should return True for valid path")
            self.assertFalse(os.path.exists(valid_file), "Valid model file should be deleted")

        finally:
             if os.path.exists(valid_file):
                os.remove(valid_file)

if __name__ == '__main__':
    unittest.main()
