import sys
import os
import time
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend import database
from backend.search import search
from backend.indexing import load_index
from backend.llm_integration import get_embeddings, get_local_llm, generate_ai_answer, get_llm_client

# Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Benchmark")

QUERY = "which companies did siddhesh worked from fractal for providing services?"
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_PATH = os.path.join(PROJECT_ROOT, 'data', 'index.faiss')
MODELS_DIR = os.path.join(PROJECT_ROOT, 'models')

def run_comparison():
    print(f"\n{'='*60}")
    print(f"BENCHMARK: {QUERY}")
    print(f"{'='*60}\n")

    # 1. Test Retrieval First
    print("--- Step 1: Testing Retrieval (Context) ---")
    if not os.path.exists(INDEX_PATH):
        print("ERROR: Index not found!")
        return

    # Load index
    try:
        index, docs, tags, index_summaries, cluster_summaries, cluster_map, bm25 = load_index(INDEX_PATH)
    except Exception as e:
        print(f"Error loading index: {e}")
        return

    # Get local embeddings
    print("Loading embeddings...")
    embeddings = get_embeddings(provider='local')
    
    # Run search
    start_t = time.time()
    results, context_snippets = search(
        QUERY, index, docs, tags, embeddings,
        index_summaries, cluster_summaries, cluster_map, bm25
    )
    search_time = time.time() - start_t
    print(f"Search completed in {search_time:.4f}s")
    
    # Analyze detailed context 
    # We want to see WHAT the model is seeing
    print(f"\nTop 3 Retrieved Chunks:")
    
    # We need to reconstruct how the context is passed to the LLM in api.py
    # API Logic: Top 1 gets smart summary, rest get raw text (roughly)
    # But for this test, let's just show the raw retrieval to see if 'Siddhesh' is even there.
    full_context_text = ""
    
    for i, res in enumerate(results[:3]):
        doc_text = res['document']
        # Try to find file path if possible (reverse lookup loop or similar? unavailable here easily without db)
        # Actually search returns 'faiss_idx', we can use database
        faiss_idx = res.get('faiss_idx')
        file_info = database.get_file_by_faiss_index(faiss_idx) if faiss_idx is not None else None
        filename = file_info['filename'] if file_info else "Unknown"
        
        print(f"\n[Result {i+1}] (File: {filename}) (Rank: {i+1})")
        print(f"Content snippet: {doc_text[:300]}...")
        
        if "siddhesh" in doc_text.lower():
            print(">>> ✅ 'Siddhesh' found in text")
        elif "siddharth" in doc_text.lower():
            print(">>> ❌ 'Siddharth' found in text (Possible Confusion)")
        else:
            print(">>> ⚠️ Neither name found explicitly in top snippet")

        full_context_text += f"Document {i+1} (from {filename}):\n{doc_text}\n\n"

    print("\n" + "="*60)
    print("--- Step 2: Testing Models (Generation) ---")
    print("Using retrieved context for all models to ensure fair comparison.")
    print("="*60)

    # Find available models
    model_files = [f for f in os.listdir(MODELS_DIR) if f.endswith('.gguf')]
    if not model_files:
        print("No local models found in models/ directory.")
        return

    for model_file in model_files:
        model_path = os.path.join(MODELS_DIR, model_file)
        print(f"\nTesting Model: {model_file}")
        print("-" * 30)

        # Force unload/reload to test initialization time
        # Note: In real app, we cache.
        
        try:
            # Measure generation
            start_gen = time.time()
            
            # We call generate_ai_answer directly, utilizing the 'local' provider path logic
            # modifying client cache key or logic to force specific model would be tricky if we rely on config
            # So we will instantiate the client directly using helper
            
            # 1. Get Client (Load Time)
            t0 = time.time()
            # We manually bypass get_llm_client caching slightly or just accept it (warmup)
            # Actually, let's use the lower level get_local_llm to ensure we test THIS specific file
            from backend.llm_integration import get_local_llm, _llm_cache, _local_llm_lock
            
            # Clear cache for this model to test fresh load? Or test cached speed?
            # User complains about "response time" -> usually includes generation. 
            # Load time only happens once. We should test WARM generation.
            
            llm = get_local_llm(model_path)
            load_time = time.time() - t0
            print(f"Load/Cache Check Time: {load_time:.4f}s")
            
            if not llm:
                print("Failed to load model.")
                continue

            # 2. Generate
            prompt = f"Context:\n{full_context_text}\n\nQuestion: {QUERY}\nAnswer:"
            
            t1 = time.time()
            with _local_llm_lock:
                 output = llm.create_completion(
                    prompt,
                    max_tokens=256,
                    stop=["Question:", "Context:"],
                    echo=False,
                    temperature=0.1 
                )
            gen_time = time.time() - t1
            response = output['choices'][0]['text'].strip()
            
            print(f"Generation Time: {colors.GREEN}{gen_time:.2f}s{colors.RESET}")
            print(f"Response: {response}\n")
            
        except Exception as e:
            print(f"Error testing model: {e}")

class colors:
    GREEN = '\033[92m'
    RESET = '\033[0m'

if __name__ == "__main__":
    # Ensure DB is init
    database.init_database()
    run_comparison()
