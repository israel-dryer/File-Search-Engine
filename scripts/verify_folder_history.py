
import requests
import json
import os

API_URL = "http://localhost:8000/api"

def test_folder_history():
    print("0. Checking API health...")
    try:
        resp = requests.get(f"{API_URL}/config")
        print(f"Health Check: {resp.status_code}")
        if resp.status_code != 200:
            print(f"Server is running but returned {resp.status_code}")
        else:
            print("Server is UP and responding to /api/config")
    except Exception as e:
        print(f"Server is DOWN or unreachable: {e}")
        return

    print("1. Checking initial history...")
    try:
        resp = requests.get(f"{API_URL}/folders/history")
        if resp.status_code != 200:
            print(f"FAILED: /folders/history returned {resp.status_code}")
            return
        initial_history = resp.json()
        print(f"Initial History: {initial_history}")
    except Exception as e:
        print(f"FAILED to connect: {e}")
        return

    print("\n2. Updating config with new folder...")
    test_folders = ["C:/Users/siddh/Documents/TestFolder1"]
    current_config_resp = requests.get(f"{API_URL}/config")
    config = current_config_resp.json()
    
    config['folders'] = test_folders
    
    resp = requests.post(f"{API_URL}/config", json=config)
    if resp.status_code == 200:
        print("Config updated successfully")
    else:
        print(f"FAILED to update config: {resp.text}")
        return

    print("\n3. Checking history after update...")
    resp = requests.get(f"{API_URL}/folders/history")
    history = resp.json()
    print(f"History: {history}")
    
    if any("TestFolder1" in p for p in history):
        print("SUCCESS: Folder added to history!")
    else:
        print("FAILED: Folder not found in history")

if __name__ == "__main__":
    test_folder_history()
