import requests
import os

API_URL = "http://localhost:8000/api"

def test_hidden_paths():
    print("Testing hidden paths...")
    
    # Check /api/config
    try:
        r = requests.get(f"{API_URL}/config")
        config = r.json()
        folders = config.get('folders', [])
        assert all("golden_dataset" not in f for f in folders), f"Found golden_dataset in folders: {folders}"
        print("[PASS] /api/config filters golden_dataset")
    except Exception as e:
        print(f"[FAIL] /api/config check: {e}")

    # Check /api/files
    try:
        r = requests.get(f"{API_URL}/api/files")
        if r.status_code == 404: # Might be /api/files or /files depending on routing
            r = requests.get(f"{API_URL}/files")
        
        files = r.json()
        assert all("golden_dataset" not in (f.get('path', '') or '') for f in files), "Found golden_dataset in files"
        print("[PASS] /api/files filters golden_dataset")
    except Exception as e:
        print(f"[ERROR] /api/files check (check if server is running): {e}")

    # Check /api/folders/history
    try:
        r = requests.get(f"{API_URL}/folders/history")
        history = r.json()
        assert all("golden_dataset" not in h for h in history), f"Found golden_dataset in history: {history}"
        print("[PASS] /api/folders/history filters golden_dataset")
    except Exception as e:
        print(f"[FAIL] /api/folders/history check: {e}")

if __name__ == "__main__":
    if not os.path.exists("backend/api.py"):
        print("Run from project root")
    else:
        test_hidden_paths()
