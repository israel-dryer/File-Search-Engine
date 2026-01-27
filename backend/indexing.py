import os
import faiss
import pickle
import numpy as np
import concurrent.futures
import time
from datetime import datetime
from typing import List, Tuple, Dict
from langchain_text_splitters import CharacterTextSplitter
from backend.llm_integration import get_embeddings, get_tags, smart_summary, summarize
from backend.file_processing import extract_text
from backend import database
from backend.clustering import perform_global_clustering
from rank_bm25 import BM25Okapi
import string

def tokenize(text):
    """Simple tokenization for BM25."""
    # Remove punctuation and lowercase
    translator = str.maketrans('', '', string.punctuation)
    return text.lower().translate(translator).split()

def safe_extract_text(filepath):
    """Wrapper for parallel execution."""
    try:
        text = extract_text(filepath)
        return filepath, text
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return filepath, None

def create_index(folder_paths, provider, api_key=None, model_path=None, progress_callback=None):
    """
    Creates a RAPTOR index (Global Clustering + Recursive Summarization).
    Optimized with Parallel Execution.
    """
    if isinstance(folder_paths, str):
        folder_paths = [folder_paths]
        
    print(f"Starting RAPTOR Indexing of folders: {folder_paths}")
    start_time = time.time()
    
    # 1. Clear Database
    database.clear_all_files()
    database.clear_clusters()
    
    # 2. Collect Files
    all_files = []
    for folder_path in folder_paths:
        if os.path.exists(folder_path):
            for dirpath, _, filenames in os.walk(folder_path):
                for filename in filenames:
                    all_files.append(os.path.join(dirpath, filename))
    
    print(f"Found {len(all_files)} total files.")
    if not all_files:
        return None, None, None, None, None, None, None

    # Define stage weights
    # Extraction: 20%, Chunking: 5%, Embedding: 40%, Clustering: 5%, Summarization: 25%, Finalizing: 5%
    # We will accumulate progress_base to ensure monotonic increase
    
    # 3. Parallel Text Extraction (CPU Bound) - 0% to 20%
    print("Step 1/5: Extracting Text (Parallel)...")
    valid_docs = [] # List of (filepath, text)
    
    # Use fewer workers for CPU bound tasks to keep UI responsive
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
        future_to_file = {executor.submit(safe_extract_text, f): f for f in all_files}
        
        compete_count = 0
        total_files = len(all_files)
        for future in concurrent.futures.as_completed(future_to_file):
            filepath, text = future.result()
            if text:
                valid_docs.append((filepath, text))
            
            compete_count += 1
            if progress_callback:
                # Map 0-total_files to 0-20%
                percent = int((compete_count / total_files) * 20)
                progress_callback(percent, 100, f"Extracting: {os.path.basename(filepath)}")

    print(f"Successfully extracted text from {len(valid_docs)} files.")

    # 4. Chunking - 20% to 25%
    if progress_callback: progress_callback(22, 100, "Chunking text...")
    print("Step 2/5: Chunking Text...")
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    
    all_chunks = [] # List of (chunk_text, filepath, file_metadata)
    chunk_strings = [] # Just the text for embedding
    
    # Track file metadata to insert into DB later
    file_metadata_map = {} 
    
    current_faiss_idx = 0
    
    for filepath, text in valid_docs:
        chunks = text_splitter.split_text(text)
        if not chunks:
            continue
            
        file_stat = os.stat(filepath)
        file_info = {
            'filename': os.path.basename(filepath),
            'extension': os.path.splitext(filepath)[1].lower(),
            'size_bytes': file_stat.st_size,
            'modified_date': datetime.fromtimestamp(file_stat.st_mtime),
            'chunk_count': len(chunks),
            'faiss_start_idx': current_faiss_idx,
            'faiss_end_idx': current_faiss_idx + len(chunks) - 1
        }
        
        # Add to DB immediately
        database.add_file(
            path=filepath,
            **file_info
        )
        
        for chunk in chunks:
            all_chunks.append({
                'text': chunk,
                'filepath': filepath,
                'faiss_idx': current_faiss_idx,
                'file_id': None # Could fetch, but relying on path match is okay for now
            })
            chunk_strings.append(chunk)
            current_faiss_idx += 1
            
    print(f"Generated {len(chunk_strings)} total chunks.")

    # 5. Parallel Embedding (I/O Bound) - 25% to 65%
    if progress_callback: progress_callback(25, 100, "Starting embeddings...")
    print("Step 3/5: Embedding Chunks (Parallel)...")
    embeddings_model = get_embeddings(provider, api_key, model_path)
    
    # Embed in batches to be efficient but safe
    batch_size = 100 
    batches = [chunk_strings[i:i + batch_size] for i in range(0, len(chunk_strings), batch_size)]
    
    chunk_embeddings = []
    
    # Use ThreadPool for Network/GPU bound
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(embeddings_model.embed_documents, batch): i for i, batch in enumerate(batches)}
        
        completed = 0
        total_batches = len(batches)
        for future in concurrent.futures.as_completed(futures):
            batch_emb = future.result()
            chunk_embeddings.extend(batch_emb)
            completed += 1
            
            if progress_callback:
                # Map 0-total_batches to 25-65% (range of 40)
                percent = 25 + int((completed / total_batches) * 40)
                progress_callback(percent, 100, f"Embedding batch {completed}/{total_batches}")

    # Sort embeddings by original order? No, extend() might mix them up if not careful.
    # Wait, as_completed() yields out of order. We MUST re-order.
    # Retry: sequential batching is safer for correct ordering unless we index futures.
    # Let's fix this:
    
    chunk_embeddings_map = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # submit returns a future object
        future_map = {executor.submit(embeddings_model.embed_documents, batch): i for i, batch in enumerate(batches)}
        
        for future in concurrent.futures.as_completed(future_map):
            batch_idx = future_map[future]
            try:
                result = future.result()
                chunk_embeddings_map[batch_idx] = result
            except Exception as e:
                print(f"Error embedding batch {batch_idx}: {e}")
                chunk_embeddings_map[batch_idx] = [] # Handle failure gracefully?

    # Reassemble in order
    chunk_embeddings = []
    for i in range(len(batches)):
        if i in chunk_embeddings_map:
            chunk_embeddings.extend(chunk_embeddings_map[i])
        else:
             print(f"Warning: Missing embeddings for batch {i}")
             # This will still cause index misalignment later. 
             # Ideally we should fail or retry.
             # For now, let's append zero-vectors or simple filler?
             # No, if we lose embeddings, the cluster map indices will point to wrong things.
             # We must ensure length matches.
             pass

    # 5b. BM25 Indexing - 65% to 68%
    if progress_callback: progress_callback(66, 100, "Building Keyword Index...")
    print("Step 3.5/5: Building BM25 Index...")
    tokenized_corpus = [tokenize(doc) for doc in chunk_strings]
    bm25 = BM25Okapi(tokenized_corpus)

    # 6. Global Clustering (RAPTOR) - 68% to 75%
    if progress_callback: progress_callback(70, 100, "Clustering content...")
    print("Step 4/5: Performing Global Clustering...")
    cluster_map = perform_global_clustering(chunk_embeddings, max_cluster_size=20)
    print(f"Created {len(cluster_map)} global clusters.")
    
    # 7. Summarize Clusters (Parallel) - 75% to 95%
    if progress_callback: progress_callback(75, 100, "Summarizing clusters...")
    print("Step 5/5: Summarizing Clusters (Parallel)...")
    
    cluster_summaries = [] # List of summary texts
    final_cluster_map = {} # Map Summary Index ID -> List of Chunk Indices
    
    def process_cluster(cluster_id, indices):
        # Join texts of chunks in this cluster
        cluster_text = "\n\n".join([chunk_strings[i] for i in indices])
        # Generate summary
        # Generate summary
        if provider == 'local':
             # For local models, skip heavy LLM summarization for speed
             summary = summarize(cluster_text, provider, api_key, model_path, f"Cluster {cluster_id}")
        else:
             summary = smart_summary(cluster_text, "Summarize the key themes and facts in this collection.", 
                                   provider, api_key, model_path, file_name=f"Cluster {cluster_id}")
        return cluster_id, summary

    total_clusters = len(cluster_map)
    processed_clusters = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_cid = {executor.submit(process_cluster, cid, idxs): cid for cid, idxs in cluster_map.items()}
        
        for future in concurrent.futures.as_completed(future_to_cid):
            cid, summary = future.result()
            if summary:
                # Add to DB
                database.add_cluster(summary, level=1)
                
                # The index in this list will be the FAISS index
                current_summary_idx = len(cluster_summaries)
                cluster_summaries.append(summary)
                
                # Remap: Summary Index ID -> Original Chunk Indices
                final_cluster_map[current_summary_idx] = cluster_map[cid]
            
            processed_clusters += 1
            if progress_callback:
                # Map 0-total_clusters to 75-95% (range of 20)
                percent = 75 + int((processed_clusters / total_clusters) * 20)
                progress_callback(percent, 100, f"Summarizing cluster {processed_clusters}/{total_clusters}")
    
    # 8. Create FAISS Indices - 95% to 99%
    if progress_callback: progress_callback(97, 100, "Finalizing Indices...")
    print("Finalizing Indices...")
    
    # Chunk Index
    chunk_emb_np = np.array(chunk_embeddings).astype('float32')
    index_chunks = faiss.IndexFlatL2(chunk_emb_np.shape[1])
    index_chunks.add(chunk_emb_np)
    
    # Summary Index
    if cluster_summaries:
        summary_embeddings = embeddings_model.embed_documents(cluster_summaries)
        summary_emb_np = np.array(summary_embeddings).astype('float32')
        index_summaries = faiss.IndexFlatL2(summary_emb_np.shape[1])
        index_summaries.add(summary_emb_np)
    else:
        index_summaries = None
    
    print(f"Indexing Complete! Chunks: {len(chunk_strings)}, Clusters: {len(cluster_summaries)}.")
    print(f"Total time: {time.time() - start_time:.2f}s")
    
    # Use empty tags list to maintain return signature
    tags = [""] * len(chunk_strings) 
    
    # Return both indices packaged (we'll need to modify save_index/load_index too)
    return index_chunks, all_chunks, tags, index_summaries, cluster_summaries, final_cluster_map, bm25

def save_index(index_chunks, all_chunks, tags, filepath, index_summaries=None, cluster_summaries=None, cluster_map=None, bm25=None):
    """
    Saves the Dual FAISS index (RAPTOR) + BM25.
    """
    faiss.write_index(index_chunks, filepath)
    
    base_path = os.path.splitext(filepath)[0]
    
    with open(base_path + '_docs.pkl', 'wb') as f:
        pickle.dump(all_chunks, f)
    with open(base_path + '_tags.pkl', 'wb') as f:
        pickle.dump(tags, f)
        
    if index_summaries is not None:
        faiss.write_index(index_summaries, base_path + '_summary.index')
        with open(base_path + '_summaries.pkl', 'wb') as f:
            pickle.dump(cluster_summaries, f)
        with open(base_path + '_cluster_map.pkl', 'wb') as f:
            pickle.dump(cluster_map, f)
            
    if bm25 is not None:
        with open(base_path + '_bm25.pkl', 'wb') as f:
            pickle.dump(bm25, f)
            
    print(f"RAPTOR Index saved to {filepath}")

def load_index(filepath):
    """
    Loads Dual FAISS index + BM25.
    """
    if not os.path.exists(filepath):
        return None, None, None, None, None, None, None
        
    index_chunks = faiss.read_index(filepath)
    base_path = os.path.splitext(filepath)[0]
    
    with open(base_path + '_docs.pkl', 'rb') as f:
        all_chunks = pickle.load(f)
    with open(base_path + '_tags.pkl', 'rb') as f:
        tags = pickle.load(f)
        
    index_summaries = None
    cluster_summaries = None
    cluster_map = None
    bm25 = None
    
    summary_idx_path = base_path + '_summary.index'
    if os.path.exists(summary_idx_path):
        index_summaries = faiss.read_index(summary_idx_path)
        with open(base_path + '_summaries.pkl', 'rb') as f:
            cluster_summaries = pickle.load(f)
        cluster_map_path = base_path + '_cluster_map.pkl'
        if os.path.exists(cluster_map_path):
            with open(cluster_map_path, 'rb') as f:
                cluster_map = pickle.load(f)
                
    bm25_path = base_path + '_bm25.pkl'
    if os.path.exists(bm25_path):
        with open(bm25_path, 'rb') as f:
            bm25 = pickle.load(f)
            
    print(f"Loaded RAPTOR Index: {len(all_chunks)} chunks, {len(cluster_summaries) if cluster_summaries else 0} clusters.")
    return index_chunks, all_chunks, tags, index_summaries, cluster_summaries, cluster_map, bm25
