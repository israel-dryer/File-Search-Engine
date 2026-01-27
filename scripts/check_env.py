try:
    from llama_cpp import Llama
    print("llama_cpp imported successfully")
    # Try to initialize with gpu_layers to see if it works or warns
    try:
        # We don't need a real model path to check if library supports it, 
        # but we do need to instantiate to check if it logs "BLAS = 1" or similar.
        # Actually better to just print the help or check for GPU.
        import os
        # simple check:
        print("Checking for CUDA/Metal support...")
        # There isn't a direct "is_gpu_available" function in python binding easily exposed without loading.
        # But we can try to load the model the user has and see if it offloads.
    except Exception as e:
        print(e)

except ImportError:
    print("llama_cpp not installed")

import multiprocessing
print(f"CPU Threads: {multiprocessing.cpu_count()}")
