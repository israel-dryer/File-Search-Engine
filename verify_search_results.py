from playwright.sync_api import sync_playwright
import time
import os

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Mock APIs
        page.route("**/api/config", lambda route: route.fulfill(json={"folders": [], "local_model_path": "test", "auto_index": False}))
        page.route("**/api/models/local", lambda route: route.fulfill(json=[{"name": "test-model", "path": "test"}]))
        page.route("**/api/index/status", lambda route: route.fulfill(json={"running": False, "progress": 0}))

        # Mock Search
        page.route("**/api/search", lambda route: route.fulfill(json={
            "results": [
                {"file_name": "doc1.pdf", "file_path": "/tmp/doc1.pdf", "document": "This is a test document content for search result 1."},
                {"file_name": "image.png", "file_path": "/tmp/image.png", "document": "This is a test document content for search result 2."}
            ],
            "active_model": "test-model"
        }))

        # Mock Stream (just return 404 or empty to stop it from hanging, or mock stream)
        # For this test, we just want to see results.
        page.route("**/api/stream-answer", lambda route: route.fulfill(body="AI Answer Content"))

        try:
            page.goto("http://localhost:5173")

            # Wait for search bar
            page.wait_for_selector("input[type='text']")

            # Type query
            page.fill("input[type='text']", "test query")
            page.press("input[type='text']", "Enter")

            # Wait for results
            page.wait_for_selector(".result-card")

            # Allow animations to settle
            time.sleep(1)

            # Take screenshot
            os.makedirs("/home/jules/verification", exist_ok=True)
            page.screenshot(path="/home/jules/verification/search_results.png")
            print("Screenshot taken at /home/jules/verification/search_results.png")

        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    run()
