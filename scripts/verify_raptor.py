import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.indexing import create_index, save_index
from backend.search import search
from backend import database
from backend.llm_integration import get_embeddings

def test_raptor_pipeline():
    print("=== Testing RAPTOR Pipeline ===")
    
    # Setup test data
    test_dir = "test_data/raptor_test"
    os.makedirs(test_dir, exist_ok=True)
    
    # Create distinct files that should cluster together
    # Cluster 1: Space
    with open(f"{test_dir}/space1.txt", "w") as f:
        f.write("Mars is the fourth planet from the Sun. It is often referred to as the 'Red Planet'.")
    with open(f"{test_dir}/space2.txt", "w") as f:
        f.write("Jupiter is the largest planet in our solar system. It is a gas giant with a mass one-thousandth that of the Sun.")
        
    # Cluster 2: Ancient Rome
    with open(f"{test_dir}/rome1.txt", "w") as f:
        f.write("The Roman Empire was the post-Republican period of ancient Rome. It included large territorial holdings around the Mediterranean Sea.")
    with open(f"{test_dir}/rome2.txt", "w") as f:
        f.write("Julius Caesar was a Roman general and statesman. A member of the First Triumvirate, Caesar led the Roman armies in the Gallic Wars.")

    # Run Indexing
    print("\n[1] Indexing...")
    # Use local provider for test speed if possible, or whatever is configured. 
    # Mocking would be better but integration test is good too.
    # Assuming 'local' or 'openai' is configured in env/config. 
    # For CI safety, we might need to mock LLM calls, but here we want to test the PIPELINE.
    # Let's mock the "smart_summary" to avoid API costs/latency for this test.
    
    import backend.llm_integration
    original_summary = backend.llm_integration.smart_summary
    
    # Mock summary to prove clustering works
    def mock_summary(text, query, provider, api_key, model_path, file_name=None):
        if "planet" in text.lower():
            return "Cluster Summary: Topics related to Planets and Space."
        if "roman" in text.lower():
            return "Cluster Summary: Topics related to Ancient History and Rome."
        return "Generic Summary"
        
    backend.llm_integration.smart_summary = mock_summary
    
    try:
        # provider='local' to avoid needing keys if possible, but embeddings needed.
        # We need a provider that works.
        # Let's try 'local' (HuggingFace) for embeddings.
        
        
        index, docs, tags, idx_sum, doc_sum, map_sum, bm25 = create_index(
            test_dir, 
            provider='local', # Forces HF Embeddings
            api_key='test',
            model_path=None
        )
        
        print(f"\n[2] Verification:")
        print(f"- Chunks: {len(docs)}")
        print(f"- Clusters: {len(doc_sum)}")
        print(f"- Map Entries: {len(map_sum)}")
        print(f"- BM25 Index: {'Built' if bm25 else 'Failed'}")
        
        if len(doc_sum) > 0:
            print(f"- Cluster 0 Summary: {doc_sum[0]}")
        
        # Test Search
        print("\n[3] Searching 'Red Planet'...")
        embeddings = get_embeddings('local')
        results, ctx = search(
            "Red Planet", 
            index, docs, tags, embeddings, 
            idx_sum, doc_sum, map_sum, bm25
        )
        
        print(f"Found {len(results)} results.")
        for r in results:
            print(f"  - {r['document'][:50]}... (Dist: {r['distance']:.4f})")
            
        # Validate that we found space1.txt
        found = any("Mars" in r['document'] for r in results)
        if found:
            print("\nSUCCESS: Found relevant document via RAPTOR search!")
        else:
            print("\nFAILURE: Did not find relevant document.")
            
    finally:
        # Restore
        backend.llm_integration.smart_summary = original_summary
        # Cleanup? 
        pass

if __name__ == "__main__":
    test_raptor_pipeline()
