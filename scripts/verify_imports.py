import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    print("Attempting to import sentence_transformers...")
    import sentence_transformers
    print(f"Success! Version: {sentence_transformers.__version__}")
    
    print("Attempting to import langchain_huggingface...")
    from langchain_huggingface import HuggingFaceEmbeddings
    print("Success! HuggingFaceEmbeddings imported.")
    
    print("Attempting to load embeddings model (this might be slow)...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    print("Success! Model loaded.")
    
except ImportError as e:
    print(f"IMPORT ERROR: {e}")
    sys.exit(1)
except Exception as e:
    print(f"RUNTIME ERROR: {e}")
    sys.exit(1)
