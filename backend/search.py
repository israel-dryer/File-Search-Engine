import faiss
import numpy as np
import concurrent.futures
from typing import List, Dict, Any, Tuple
import string

# Optimized stop words list for fast filtering
STOP_WORDS = {
    'a', 'an', 'the', 'and', 'or', 'but', 'if', 'then', 'else', 'when', 'at', 'by', 'from', 'for', 'with', 'in', 'on', 'to', 'is', 'am', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'but', 'so', 'up', 'down', 'out', 'off', 'over', 'under', 'again', 'further', 'once', 'here', 'there', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'than', 'too', 'very', 'can', 'will', 'just', 'should', 'now'
}

def tokenize(text):
    """Refined tokenization for BM25 with stop-word filtering."""
    if not text: return []
    translator = str.maketrans('', '', string.punctuation)
    tokens = text.lower().translate(translator).split()
    return [t for t in tokens if t not in STOP_WORDS and len(t) > 1]

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
    keyword_candidates = {} # idx -> score
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        # Start Parallel Tasks
        future_chunks = executor.submit(index.search, query_embedding, 15) # Top 15 direct
        
        future_summaries = None
        if index_summaries:
            future_summaries = executor.submit(index_summaries.search, query_embedding, 3) # Top 3 themes
            
        future_bm25 = None
        if bm25:
            tokenized_query = tokenize(query)
            future_bm25 = executor.submit(bm25.get_scores, tokenized_query)
            
        # Process Chunk Results
        dists_c, idxs_c = future_chunks.result()
        for i, idx in enumerate(idxs_c[0]):
            if idx != -1:
                vector_candidates[int(idx)] = float(dists_c[0][i])
        
        # Process Keyword Results
        if future_bm25:
            try:
                scores = future_bm25.result()
                top_n = np.argsort(scores)[::-1][:20]
                for idx in top_n:
                    if scores[idx] > 0:
                        keyword_candidates[int(idx)] = float(scores[idx])
            except Exception as e:
                print(f"BM25 Parallel Error: {e}")

        # Process Summary -> Expansion
        if future_summaries and cluster_map:
            dists_s, idxs_s = future_summaries.result()
            for i, idx in enumerate(idxs_s[0]):
                if idx != -1:
                    child_indices = cluster_map.get(int(idx), [])
                    for child_idx in child_indices:
                        if child_idx < len(docs):
                            if int(child_idx) not in vector_candidates:
                                vector_candidates[int(child_idx)] = 100.0 # Placeholder distance

    # 3. Reciprocal Rank Fusion (RRF)
    # RRF Score = 1 / (k + rank)
    k = 60
    final_scores = {} # idx -> rrf_score

    print(f"\n[SEARCH] Query: '{query}'")
    print(f"[SEARCH] Found {len(vector_candidates)} semantic and {len(keyword_candidates)} keyword candidates.")
    
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

    # 4. Identity/Exact Match Boost
    # If a query contains a potential name, boost documents that contain that exact string
    # This helps distinguish between 'Siddhesh' and 'Siddharth'
    query_terms = [t for t in tokenize(query) if len(t) > 3]
    boost_count = 0
    for idx in final_scores:
        doc_info = docs[idx]
        doc_text = doc_info.get('text', "") if isinstance(doc_info, dict) else str(doc_info)
        doc_text = doc_text.lower()
        for term in query_terms:
            if term in doc_text:
                # Small boost for each matching term from query
                final_scores[idx] *= 1.1
                boost_count += 1
    
    if boost_count > 0:
        print(f"[SEARCH] Applied Identity Boost to {boost_count} matches.")
        
    # 5. Sort by RRF Score (Higher is better)
    sorted_final = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
    top_indices = [idx for idx, score in sorted_final[:10]] # Top 10 fused
    print(f"[SEARCH] Returning top {len(top_indices)} fused results.")
    
    # 4. Format Results
    results = []
    context_snippets = []
    
    seen_files = {} # path -> count
    
    for rank, idx in enumerate(top_indices):
        doc_info = docs[idx]
        doc_text = doc_info.get('text', "") if isinstance(doc_info, dict) else str(doc_info)
        file_path = doc_info.get('filepath', "") if isinstance(doc_info, dict) else None
        
        # Diversity check: Skip if we already have 2 chunks from this file
        # unless we are running low on total results
        if file_path:
            count = seen_files.get(file_path, 0)
            if count >= 2 and len(results) < 5: 
                 # Soft limit: allow more if we have very few results so far
                 pass
            elif count >= 2:
                 continue # Skip this chunk to show other files
            seen_files[file_path] = count + 1
        
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
        
        if len(results) >= 10:
            break
            
    return results, context_snippets
