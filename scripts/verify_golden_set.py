
import os
import requests
import time
import sys
import json
from pprint import pprint

# Backend URL
API_URL = "http://localhost:8000/api"
GOLDEN_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "golden_dataset")

def wait_for_backend():
    print("Checking backend status...")
    for _ in range(10):
        try:
            r = requests.get(f"{API_URL}/config", timeout=2)
            if r.status_code == 200:
                print("Backend is ready.")
                return True
        except:
            time.sleep(1)
    return False

def configure_folder():
    """Add golden_dataset folder to configuration."""
    print(f"Adding {GOLDEN_DIR} to config...")
    # Get current config
    r = requests.get(f"{API_URL}/config")
    current_config = r.json()
    folders = current_config.get('folders', [])
    
    if GOLDEN_DIR not in folders:
        folders.append(GOLDEN_DIR)
        requests.post(f"{API_URL}/config", json={**current_config, "folders": folders})
        print("Folder added.")
    else:
        print("Folder already configured.")

def trigger_indexing():
    """Trigger indexing and wait for completion."""
    print("Triggering index...")
    requests.post(f"{API_URL}/index")
    
    # Poll status
    while True:
        r = requests.get(f"{API_URL}/index/status")
        status = r.json()
        if not status['running']:
            print("Indexing complete.")
            break
        print(f"Indexing: {status['progress']}%...")
        time.sleep(2)

def verify_query(query, expected_text, filename):
    """Run a search query and verify the expected text is in the summary/answer."""
    print(f"\nQuerying: '{query}'...")
    r = requests.post(f"{API_URL}/search", json={"query": query})
    if r.status_code != 200:
        print(f"Search failed: {r.status_code}")
        return False
        
    data = r.json()
    results = data.get('results', [])
    ai_answer = data.get('ai_answer', '')
    
    found_in_results = False
    for res in results:
        if filename in str(res.get('file_name', '')) or filename in str(res.get('file_path', '')):
            if expected_text.lower() in res.get('summary', '').lower() or expected_text.lower() in res.get('document', '').lower():
                found_in_results = True
                break
                
    found_in_answer = expected_text.lower() in ai_answer.lower()
    
    print(f"  > Found in Results: {found_in_results}")
    print(f"  > Found in AI Answer: {found_in_answer}")
    
    if found_in_results or found_in_answer:
        print("  [PASS] Needle found!")
        return True
    else:
        print(f"  [FAIL] Expected '{expected_text}' not found.")
        return False

def main():
    if not wait_for_backend():
        print("Backend not running. Please start it with 'npm run start'.")
        sys.exit(1)
        
    configure_folder()
    trigger_indexing()
    
    # Test Cases (Needle in Haystack)
    tests = [
        ("What is the population of Clouded Leopards?", "10,000", "synthetic_nature.pdf"),
        ("What is the Q3 growth in Asia?", "18%", "synthetic_sales.xlsx"),
        ("What is the Q3 goal for Project Phoenix?", "Launch MVP", "synthetic_roadmap.pptx"),
        ("What percent of enterprises plan to adopt AI agents?", "85%", "synthetic_report.docx")
    ]
    
    passed = 0
    for q, expected, fname in tests:
        if verify_query(q, expected, fname):
            passed += 1
            
    print(f"\nTotal Result: {passed}/{len(tests)} tests passed.")
    if passed == len(tests):
        print("ALL GOLDEN DATASET TESTS PASSED. 🚀")
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
