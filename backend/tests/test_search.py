import unittest
import numpy as np
from unittest.mock import MagicMock
from backend.search import search


class TestSearch(unittest.TestCase):
    """Test cases for search module"""

    def test_search_basic(self):
        """Test basic search functionality."""
        # Create mock embeddings model
        mock_embeddings_model = MagicMock()
        mock_embeddings_model.embed_query.return_value = [0.5, 0.5, 0.5]
        
        # Create mock index
        import faiss
        dimension = 3
        index = faiss.IndexFlatL2(dimension)
        embeddings = np.array([
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6],
            [0.7, 0.8, 0.9]
        ], dtype='float32')
        index.add(embeddings)
        
        # Documents and tags
        docs = ["Document 1", "Document 2", "Document 3"]
        tags = ["tag1", "tag2", "tag3"]
        
        # Perform search
        query = "test query"
        results, context = search(query, index, docs, tags, mock_embeddings_model)
        
        # Verify results
        self.assertEqual(len(results), 3)  # Should return up to 10 results, but we only have 3 docs
        self.assertIsInstance(results, list)
        self.assertIsInstance(context, list)
        
        # Check structure of each result
        for result in results:
            self.assertIn("document", result)
            self.assertIn("distance", result)
            self.assertIn("tags", result)
            self.assertIsInstance(result["document"], str)
            self.assertIsInstance(result["distance"], (int, float, np.floating))
            self.assertIsInstance(result["tags"], list)
    
    def test_search_with_more_documents_than_k(self):
        """Test search when there are more documents than k (top results)."""
        # Create mock embeddings model
        mock_embeddings_model = MagicMock()
        mock_embeddings_model.embed_query.return_value = [0.5, 0.5, 0.5]
        
        # Create mock index with many documents
        import faiss
        dimension = 3
        index = faiss.IndexFlatL2(dimension)
        embeddings = np.array([
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6],
            [0.7, 0.8, 0.9],
            [0.2, 0.3, 0.4],
            [0.5, 0.6, 0.7],
            [0.8, 0.9, 1.0]
        ], dtype='float32')
        index.add(embeddings)
        
        # Many documents and tags
        docs = [f"Document {i}" for i in range(6)]
        tags = [f"tag{i}" for i in range(6)]
        
        # Perform search
        query = "test query"
        results, context = search(query, index, docs, tags, mock_embeddings_model)
        
        # Should return top 10 results if available, here we have 6 docs
        self.assertEqual(len(results), 6)
    
    def test_search_with_insufficient_documents(self):
        """Test search when there are fewer documents than requested."""
        # Create mock embeddings model
        mock_embeddings_model = MagicMock()
        mock_embeddings_model.embed_query.return_value = [0.5, 0.5, 0.5]
        
        # Create mock index with only one document
        import faiss
        dimension = 3
        index = faiss.IndexFlatL2(dimension)
        embeddings = np.array([[0.1, 0.2, 0.3]], dtype='float32')
        index.add(embeddings)
        
        # Single document and tag
        docs = ["Single Document"]
        tags = ["single_tag"]
        
        # Perform search
        query = "test query"
        results, context = search(query, index, docs, tags, mock_embeddings_model)
        
        # Should return the single document
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["document"], "Single Document")
        # tags_list contains "Semantic" by default in search.py if found in vector search
        self.assertIn("Semantic", results[0]["tags"])
        self.assertIn("single_tag", results[0]["tags"])
    
    def test_search_empty_index(self):
        """Test search with an empty index."""
        # Create mock embeddings model
        mock_embeddings_model = MagicMock()
        mock_embeddings_model.embed_query.return_value = [0.5, 0.5, 0.5]
        
        # Create empty index
        import faiss
        dimension = 3
        index = faiss.IndexFlatL2(dimension)
        
        # Empty documents and tags
        docs = []
        tags = []
        
        # Perform search
        query = "test query"
        results, context = search(query, index, docs, tags, mock_embeddings_model)
        
        # Should return empty results
        self.assertEqual(len(results), 0)


if __name__ == '__main__':
    unittest.main()
