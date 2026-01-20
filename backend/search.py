import faiss
import numpy as np

def search(query, index, docs, tags, embeddings_model):
    """
    Performs a semantic search on the index.
    """
    query_embedding = np.array([embeddings_model.embed_query(query)]).astype('float32')
    distances, indices = index.search(query_embedding, k=5) # Return top 5 results

    results = []
    for i, idx in enumerate(indices[0]):
        # Check if idx is a valid index and not -1 (which FAISS returns for empty indices)
        if idx != -1 and idx < len(docs):
            # Handle tags as either a string or a list
            tag = tags[idx] if idx < len(tags) else []
            # If tag is a list, join it; otherwise use as-is
            if isinstance(tag, list):
                tag = ', '.join(tag)
            results.append({
                "document": docs[idx],
                "distance": float(distances[0][i]),
                "tags": tag,
                "faiss_idx": int(idx)
            })

    return results

