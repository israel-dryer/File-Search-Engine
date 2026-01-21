import faiss
import numpy as np
import concurrent.futures
from typing import List, Dict, Any, Tuple

def search(query: str, index, docs: List[Dict], tags: List[str], embeddings_model, 
           index_summaries=None, cluster_summaries=None, cluster_map=None) -> List[Dict]:
    """
    Performs a RAPTOR search:
    1. Parallel search of Chunk Index and Summary Index.
    2. Expand matching clusters to include their child chunks.
    3. Rerank all candidates (Direct hits + Cluster children) against the query.
    4. Return top results.
    """
    query_embedding = np.array([embeddings_model.embed_query(query)]).astype('float32')
    
    # 1. Parallel Search
    chunks_results = []
    summaries_results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_chunks = executor.submit(index.search, query_embedding, 10) # Top 10 direct
        
        future_summaries = None
        if index_summaries:
            future_summaries = executor.submit(index_summaries.search, query_embedding, 2) # Top 2 themes
            
        # Wait for results
        dists_c, idxs_c = future_chunks.result()
        chunks_results = list(zip(idxs_c[0], dists_c[0]))
        
        if future_summaries:
            dists_s, idxs_s = future_summaries.result()
            summaries_results = list(zip(idxs_s[0], dists_s[0]))

    # 2. Candidate Collection & Expansion
    candidate_indices = set()
    
    # Add direct chunk hits
    for idx, dist in chunks_results:
        if idx != -1:
            candidate_indices.add(int(idx))
            
    # Add cluster children (RAPTOR Expansion)
    # If a summary matches well, its children are likely relevant context
    if cluster_map:
        for idx, dist in summaries_results:
            if idx != -1:
                # Get children from map (Summary ID -> Chunk IDs)
                child_indices = cluster_map.get(int(idx), [])
                # Add all children? Or verify?
                # Optimization: Add all, we will rerank them. 
                # Limit: If cluster is huge, maybe sample? But our max_cluster_size is 20, so it's fine.
                for child_idx in child_indices:
                    candidate_indices.add(int(child_idx))

    # 3. Rerank Candidates
    # We need to score all candidates against the query_embedding
    if not candidate_indices:
        return []
        
    candidates = list(candidate_indices)
    
    # Check bounds
    candidates = [i for i in candidates if i < len(docs)]
    
    if not candidates:
        return []

    # Get vectors for candidates
    # faiss.IndexFlatL2 supports reconstruction
    try:
        candidate_vectors = np.array([index.reconstruct(i) for i in candidates])
        
        # Calculate distances (L2) - smaller is better
        # distance = ||q - v||^2
        diff = candidate_vectors - query_embedding
        dists = np.sum(diff**2, axis=1)
        
        # Sort by distance
        sorted_indices = np.argsort(dists)
        top_indices = [candidates[i] for i in sorted_indices[:10]] # Top 10 final
        top_dists = [dists[i] for i in sorted_indices[:10]]
        
    except Exception as e:
        print(f"Reranking failed (index might not support reconstruct): {e}")
        # Fallback to direct chunks results if reconstruction fails
        top_indices = [int(i) for i, d in chunks_results if i != -1]
        top_dists = [float(d) for i, d in chunks_results if i != -1]

    # 4. Format Results
    results = []
    for i, idx in enumerate(top_indices):
        doc_info = docs[idx] # This is a dict {'text':..., 'filepath':..., ...}
        
        # Handle tags
        tag = tags[idx] if idx < len(tags) else []
        if isinstance(tag, list):
            tag = ', '.join(tag)
            
        # doc_info is {text, filepath, ...} or just string?
        # In indexing.py: all_chunks.append({'text': chunk, 'filepath':...})
        # So docs[idx] is a dict.
        
        doc_text = doc_info.get('text', "") if isinstance(doc_info, dict) else str(doc_info)
        file_path = doc_info.get('filepath', "") if isinstance(doc_info, dict) else None
        file_name = None
        if file_path:
             file_name = file_path.split("/")[-1].split("\\")[-1]

        results.append({
            "document": doc_text,
            "distance": float(top_dists[i]),
            "tags": tag,
            "faiss_idx": int(idx),
            "file_path": file_path,
            "file_name": file_name
        })
        
    return results
