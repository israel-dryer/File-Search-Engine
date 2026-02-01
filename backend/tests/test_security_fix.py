import pytest
import os
import tempfile
import shutil
from backend.model_manager import delete_model, is_safe_path

@pytest.fixture
def temp_models_dir(monkeypatch):
    # Create a temp directory to act as MODELS_DIR
    temp_dir = tempfile.mkdtemp()

    # Patch MODELS_DIR in backend.model_manager
    monkeypatch.setattr("backend.model_manager.MODELS_DIR", temp_dir)

    yield temp_dir

    # Cleanup
    shutil.rmtree(temp_dir)

def test_is_safe_path_valid():
    with tempfile.TemporaryDirectory() as base_dir:
        file_path = os.path.join(base_dir, "file.txt")
        assert is_safe_path(base_dir, file_path) is True

def test_is_safe_path_traversal():
    with tempfile.TemporaryDirectory() as base_dir:
        # Create a sibling directory
        sibling_dir = base_dir + "_sibling"
        os.makedirs(sibling_dir, exist_ok=True)
        try:
            target_path = os.path.join(sibling_dir, "secret.txt")

            # Using .. to go out of base_dir
            # e.g. /tmp/tmpxxx/../tmpxxx_sibling/secret.txt
            traversal_path = os.path.join(base_dir, "..", os.path.basename(sibling_dir), "secret.txt")

            # Should be False because it resolves to sibling_dir which is not under base_dir
            assert is_safe_path(base_dir, traversal_path) is False
        finally:
            if os.path.exists(sibling_dir):
                shutil.rmtree(sibling_dir)

def test_delete_model_valid(temp_models_dir):
    # Create a file inside temp_models_dir
    model_path = os.path.join(temp_models_dir, "test_model.gguf")
    with open(model_path, "w") as f:
        f.write("data")

    assert delete_model(model_path) is True
    assert not os.path.exists(model_path)

def test_delete_model_outside(temp_models_dir):
    # Create a file outside
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        outside_path = tmp.name
        tmp.write(b"data")

    try:
        # Attempt to delete explicit outside path
        assert delete_model(outside_path) is False
        assert os.path.exists(outside_path)
    finally:
        if os.path.exists(outside_path):
            os.remove(outside_path)

def test_delete_model_traversal(temp_models_dir):
    # Create a file outside
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        outside_path = tmp.name
        tmp.write(b"data")

    try:
        # Construct path using traversal from temp_models_dir
        # path = models/../../tmp/file

        rel_path = os.path.relpath(outside_path, temp_models_dir)
        traversal_path = os.path.join(temp_models_dir, rel_path)

        # Verify our traversal path actually points to the file (sanity check)
        assert os.path.exists(traversal_path)

        # But delete_model should reject it
        assert delete_model(traversal_path) is False
        assert os.path.exists(outside_path)
    finally:
        if os.path.exists(outside_path):
            os.remove(outside_path)

def test_delete_model_nonexistent(temp_models_dir):
    path = os.path.join(temp_models_dir, "fake.gguf")
    assert delete_model(path) is False
