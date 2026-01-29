import time
import sys
import os

print(f"[{time.time()}] Starting import test...")
start = time.time()

# Mock settings to avoid side effects if needed (though we want to test real startup)
os.environ['TEST_MODE'] = '1'

import backend.api

print(f"[{time.time()}] 'backend.api' imported in {time.time() - start:.4f}s")
print(f"Loaded modules: {len(sys.modules)}")

# Check for heavy modules
heavy_modules = ['torch', 'numpy', 'llama_cpp', 'langchain', 'faiss', 'tensorflow', 'transformers']
for m in heavy_modules:
    detected = [name for name in sys.modules if name.startswith(m)]
    if detected:
        print(f"WARNING: '{m}' was imported! ({len(detected)} submodules)")
    else:
        print(f"OK: '{m}' was NOT imported.")
