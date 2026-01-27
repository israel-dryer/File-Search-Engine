import requests
import time
import sys

API_URL = "http://127.0.0.1:8000/api"

def check_backend():
    print("Waiting for backend to start...")
    for i in range(12):  # Try for 60 seconds
        try:
            requests.get(f"{API_URL}/config", timeout=5)
            print("Backend is online!")
            return True
        except:
            print(f"Backend unavailable, retrying ({i+1}/12)...")
            time.sleep(5)
    return False

def trigger_indexing():
    print("Triggering index...")
    requests.post(f"{API_URL}/index")
    
    while True:
        status = requests.get(f"{API_URL}/index/status").json()
        print(f"Progress: {status['progress']}% - {status['current_file']}")
        if not status['running']:
            if status.get('error'):
                print(f"Indexing Error: {status['error']}")
                return False
            return True
        time.sleep(2)

def query_system():
    query = "did siddhesh work at google?"
    print(f"\nQuerying: {query}")
    
    # Use the /api/search endpoint (non-streaming for script simplicity)
    # The user manual mentioned /api/search with AI summaries
    resp = requests.post(f"{API_URL}/search", json={
        "query": query,
        "mode": "hybrid", 
        "include_summary": True
    })
    
    if resp.status_code != 200:
        print(f"Search Failed: {resp.text}")
        return False
        
    data = resp.json()
    answer = data.get('summary', '') or data.get('ai_answer', '')
    print(f"\nAI Answer: {answer}\n")
    
    expected_keywords = ["google", "uk", "year"]
    lower_answer = answer.lower()
    
    missing = [k for k in expected_keywords if k not in lower_answer]
    
    if not missing:
        print("✅ SUCCESS: Answer contains verifiable facts.")
        return True
    else:
        print(f"❌ FAILURE: Answer missing keywords: {missing}")
        return False

def check_history():
    print("\nChecking History...")
    resp = requests.get(f"{API_URL}/folders/history")
    folders = resp.json()
    print(f"History Folders: {folders}")
    if folders:
        print("✅ History populated.")
    else:
        print("❌ History empty - Verify 'mark_folder_indexed' logic.")

if __name__ == "__main__":
    if not check_backend():
        print("Backend not running!")
        sys.exit(1)
        
    if trigger_indexing():
        check_history()
        query_system()
