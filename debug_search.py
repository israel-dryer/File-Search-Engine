
import sys
import os
import pickle
import re

# Add project root to path
sys.path.append(os.getcwd())

def analyze_resume_chunks():
    print("Loading index_docs.pkl...")
    try:
        with open('data/index_docs.pkl', 'rb') as f:
            docs = pickle.load(f)
        
        print(f"Loaded {len(docs)} documents.")
        
        resume_chunks = []
        for i, doc in enumerate(docs):
            path = doc.get('filepath', '')
            if 'resume' in path.lower() or 'siddhesh' in path.lower():
                resume_chunks.append((i, doc))
        
        print(f"\nFound {len(resume_chunks)} chunks for Resume/Siddhesh:")
        
        for i, doc in resume_chunks:
            text = doc.get('text', '')
            path = doc.get('filepath', '')
            print(f"\n--- Chunk {i} ({path}) ---")
            print(f"Length: {len(text)} chars")
            print("-" * 20 + " START TEXT " + "-" * 20)
            # Print first 500 chars clean
            print(text[:500].replace('\n', ' '))
            print("-" * 20 + " END TEXT " + "-" * 20)
            
            # Print keywords found context
            query_terms = ["work", "experience", "employment", "company", "job"]
            print("\nKeywords found:")
            for term in query_terms:
                if term in text.lower():
                    # Find and print context
                    idx = text.lower().find(term)
                    start = max(0, idx - 30)
                    end = min(len(text), idx + 30)
                    print(f"  - '{term}': ...{text[start:end].replace(chr(10), ' ')}...")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_resume_chunks()
