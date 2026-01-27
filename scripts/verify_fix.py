
import os
import sys
import logging
import requests
import time

# 1. Verify sentence-transformers
print("--- Verifying sentence-transformers ---")
try:
    from sentence_transformers import SentenceTransformer
    print("SUCCESS: sentence-transformers imported successfully.")
    # Optional: Load a tiny model if possible, but import is usually enough validity
except ImportError as e:
    print(f"FAILURE: Could not import sentence_transformers: {e}")
    sys.exit(1)

# 2. Verify Logging File Creation
print("\n--- Verifying Logging File ---")
# Script is in scripts/, so project root is one level up
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
LOG_PATH = os.path.join(DATA_DIR, 'app.log')

# Ensure config is set to look for api in backend
sys.path.append(PROJECT_ROOT)

# We can't easily run the FastAPI app here to generate logs without blocking, 
# but we can try to hit the endpoint if the server was running. 
# Since we are in a script, we will simulate the backend logging setup logic.

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("test_logger")
logger.info("TEST LOG ENTRY - If you see this in app.log, logging is working.")

if os.path.exists(LOG_PATH):
    print(f"SUCCESS: Log file found at {LOG_PATH}")
    with open(LOG_PATH, 'r') as f:
        content = f.read()
        if "TEST LOG ENTRY" in content:
            print("SUCCESS: Test log entry found in file.")
        else:
            print("FAILURE: Test log entry NOT found in file.")
else:
    print(f"FAILURE: Log file not found at {LOG_PATH}")

print("\n--- Verification Complete ---")
