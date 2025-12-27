import os
import faiss
import pickle
import numpy as np
from datetime import datetime
from langchain_text_splitters import CharacterTextSplitter
from llm_integration import get_embeddings, get_tags
from file_processing import extract_text
import database

def create_index(folder_paths, provider, api_key=None, model_path=None, progress_callback=None):
    """
    Creates a FAISS index for the files in the specified folders.
    Now with metadata storage and progress tracking across multiple folders.
    """
    if isinstance(folder_paths, str):
        folder_paths = [folder_paths]
        
    print(f"Starting indexing of folders: {folder_paths}")
    
    embeddings_model = get_embeddings(provider, api_key, model_path)
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)

    # Clear existing files from database
    database.clear_all_files()
    
    # Collect all files first from all folders
    all_files = []
    for folder_path in folder_paths:
        if not os.path.exists(folder_path):
            print(f"Warning: Folder does not exist: {folder_path}")
            continue
        for dirpath, _, filenames in os.walk(folder_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                all_files.append(filepath)
    
    print(f"Found {len(all_files)} total files to process")
    
    if not all_files:
        print("No files found in any of the folders")
        return None, None, None
    
    docs = []
    tags = []
    current_faiss_idx = 0
    
    for i, filepath in enumerate(all_files):
        try:
            # Report progress
            if progress_callback:
                progress_callback(i + 1, len(all_files), os.path.basename(filepath))
            
            print(f"Processing {i+1}/{len(all_files)}: {filepath}")
            
            # Get file metadata
            file_stat = os.stat(filepath)
            file_size = file_stat.st_size
            modified_date = datetime.fromtimestamp(file_stat.st_mtime)
            filename = os.path.basename(filepath)
            extension = os.path.splitext(filepath)[1].lower()
            
            # Extract text
            text = extract_text(filepath)
            if not text:
                print(f"  Skipped: No text extracted")
                continue
            
            # Split into chunks
            chunks = text_splitter.split_text(text)
            chunk_count = len(chunks)
            
            if chunk_count == 0:
                print(f"  Skipped: No chunks created")
                continue
            
            print(f"  Created {chunk_count} chunks")
            
            # Store chunks
            faiss_start_idx = current_faiss_idx
            faiss_end_idx = current_faiss_idx + chunk_count - 1
            
            docs.extend(chunks)
            
            # Generate tags for first chunk only (to save time)
            first_chunk_tags = get_tags(chunks[0], provider, api_key, model_path)
            doc_tags_list = [tag.strip() for tag in first_chunk_tags.split(',') if tag.strip()]
            
            # Use same tags for all chunks of this file
            for _ in range(chunk_count):
                tags.append(doc_tags_list[:5] if doc_tags_list else [])
            
            # Store metadata in database
            database.add_file(
                path=filepath,
                filename=filename,
                extension=extension,
                size_bytes=file_size,
                modified_date=modified_date,
                chunk_count=chunk_count,
                faiss_start_idx=faiss_start_idx,
                faiss_end_idx=faiss_end_idx
            )
            
            current_faiss_idx += chunk_count
            print(f"  Successfully indexed: {chunk_count} chunks")
            
        except Exception as e:
            print(f"  Error processing {filepath}: {e}")
            continue

    if not docs:
        print("No documents were successfully processed")
        return None, None, None

    print(f"Creating FAISS index with {len(docs)} total chunks")
    embeddings = np.array(embeddings_model.embed_documents(docs)).astype('float32')

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    
    print(f"Indexing complete: {len(docs)} document chunks from {len(all_files)} files")
    return index, docs, tags

def save_index(index, docs, tags, filepath):
    """
    Saves the FAISS index and documents to a file.
    """
    import os
    faiss.write_index(index, filepath)
    docs_path = os.path.splitext(filepath)[0] + '_docs.pkl'
    tags_path = os.path.splitext(filepath)[0] + '_tags.pkl'
    with open(docs_path, 'wb') as f:
        pickle.dump(docs, f)
    with open(tags_path, 'wb') as f:
        pickle.dump(tags, f)
    print(f"Index saved to {filepath}")

def load_index(filepath):
    """
    Loads a FAISS index and documents from a file.
    """
    import os
    index = faiss.read_index(filepath)
    docs_path = os.path.splitext(filepath)[0] + '_docs.pkl'
    tags_path = os.path.splitext(filepath)[0] + '_tags.pkl'
    with open(docs_path, 'rb') as f:
        docs = pickle.load(f)
    with open(tags_path, 'rb') as f:
        tags = pickle.load(f)
    print(f"Index loaded from {filepath}: {len(docs)} chunks")
    return index, docs, tags
