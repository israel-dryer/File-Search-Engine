import faiss
import numpy as np
import concurrent.futures
from typing import List, Dict, Any, Tuple
import string

def tokenize(text):
    """Simple tokenization for BM25."""
    translator = str.maketrans('', '', string.punctuation)
    return text.lower().translate(translator).split()

def search(query: str, index, docs: List[Dict], tags: List[str], embeddings_model, 
           index_summaries=None, cluster_summaries=None, cluster_map=None, bm25=None) -> Tuple[List[Dict], List[str]]:
    """
    Performs Hybrid Search (RAPTOR + BM25) using Reciprocal Rank Fusion (RRF).
    Returns:
        results: List of result dicts
        context_snippets: List of text snippets for AI generation
    """
    
    # 1. Start Vector Search (Parallel Chunk + Summary)
    query_embedding = np.array([embeddings_model.embed_query(query)]).astype('float32')
    
    vector_candidates = {} # idx -> score (distance)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_chunks = executor.submit(index.search, query_embedding, 15) # Top 15 direct
        
        future_summaries = None
        if index_summaries:
            future_summaries = executor.submit(index_summaries.search, query_embedding, 3) # Top 3 themes
            
        # Process Chunk Results
        dists_c, idxs_c = future_chunks.result()
        for i, idx in enumerate(idxs_c[0]):
            if idx != -1:
                vector_candidates[int(idx)] = float(dists_c[0][i])
        
        # Process Summary -> Expansion
        if future_summaries and cluster_map:
            dists_s, idxs_s = future_summaries.result()
            for i, idx in enumerate(idxs_s[0]):
                if idx != -1:
                    child_indices = cluster_map.get(int(idx), [])
                    for child_idx in child_indices:
                        if child_idx < len(docs):
                            # Assign a default good score if not found directly? 
                            # Or just add to candidates for reranking.
                            # For RRF, we need a rank.
                            # Expansion strategy: these act as "Semantic Hits"
                            if int(child_idx) not in vector_candidates:
                                vector_candidates[int(child_idx)] = 100.0 # Placeholder distance
    
    # 2. BM25 Search (Keyword)
    keyword_candidates = {} # idx -> score
    if bm25:
        tokenized_query = tokenize(query)
        # get_scores gives score for every doc. Efficient?
        # For small local dataset (<100k docs), yes.
        # For larger, get_top_n is better but we need indices.
        # bm25.get_scores() returns array in order of corpus.
        
        # Optim: If many docs, this might be slow. 
        # But we are local.
        try:
             scores = bm25.get_scores(tokenized_query)
             # Get top 20 indices
             top_n = np.argsort(scores)[::-1][:20]
             for idx in top_n:
                 if scores[idx] > 0:
                     keyword_candidates[int(idx)] = float(scores[idx])
        except Exception as e:
            print(f"BM25 Error: {e}")

    # 3. Reciprocal Rank Fusion (RRF)
    # RRF Score = 1 / (k + rank)
    k = 60
    final_scores = {} # idx -> rrf_score
    
    # Rank Vector Results (Lower distance is better)
    sorted_vector = sorted(vector_candidates.items(), key=lambda x: x[1])
    for rank, (idx, dist) in enumerate(sorted_vector):
        if idx not in final_scores: final_scores[idx] = 0.0
        final_scores[idx] += 1 / (k + rank + 1)
        
    # Rank Keyword Results (Higher score is better)
    sorted_keyword = sorted(keyword_candidates.items(), key=lambda x: x[1], reverse=True)
    for rank, (idx, score) in enumerate(sorted_keyword):
        if idx not in final_scores: final_scores[idx] = 0.0
        final_scores[idx] += 1 / (k + rank + 1)
        
    # Sort by RRF Score (Higher is better)
    sorted_final = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
    top_indices = [idx for idx, score in sorted_final[:10]] # Top 10 fused
    
    # 4. Format Results
    results = []
    context_snippets = []
    
    for rank, idx in enumerate(top_indices):
        doc_info = docs[idx]
        doc_text = doc_info.get('text', "") if isinstance(doc_info, dict) else str(doc_info)
        file_path = doc_info.get('filepath', "") if isinstance(doc_info, dict) else None
        
        file_name = None
        if file_path:
             file_name = file_path.split("/")[-1].split("\\")[-1]

        # Determine source (Vector or Keyword or Both)
        tags_list = []
        if idx in vector_candidates: tags_list.append("Semantic")
        if idx in keyword_candidates: tags_list.append("Keyword")
        
        # Add original tags
        orig_tag = tags[idx] if idx < len(tags) else []
        if isinstance(orig_tag, list):
            tags_list.extend(orig_tag)
        elif isinstance(orig_tag, str) and orig_tag:
            tags_list.append(orig_tag)
            
        results.append({
            "document": doc_text,
            "distance": 0.0, # RRF doesn't have distance, use 0 or fake it
            "tags": tags_list,
            "faiss_idx": int(idx),
            "file_path": file_path,
            "file_name": file_name
        })
        
        # Prepare context for AI
        context_snippets.append(doc_text)
        
    return results, context_snippets
