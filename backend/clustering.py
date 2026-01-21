import numpy as np
from sklearn.cluster import KMeans
from typing import List, Dict

def perform_global_clustering(embeddings: List[List[float]], max_cluster_size: int = 20) -> Dict[int, List[int]]:
    """
    Groups embeddings into clusters using K-Means.
    Returns: {cluster_id: [chunk_index_1, chunk_index_2, ...]}
    """
    if not embeddings:
        return {}
    
    # Convert to numpy array
    X = np.array(embeddings)
    n_samples = X.shape[0]
    
    # Determine number of clusters
    # Heuristic: We want approx 'max_cluster_size' items per cluster
    n_clusters = max(1, n_samples // max_cluster_size)
    
    # Cap n_clusters to avoid over-fragmentation (e.g. at least 2 clusters if we have > 20 items)
    if n_samples <= max_cluster_size:
        return {0: list(range(n_samples))} # Single cluster
        
    print(f"Clustering {n_samples} items into {n_clusters} clusters...")
    
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X)
    
    # Group indices by label
    clusters = {}
    for i, label in enumerate(labels):
        label = int(label)
        if label not in clusters:
            clusters[label] = []
        clusters[label].append(i)
        
    return clusters
