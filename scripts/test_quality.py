"""Compare TinyLlama vs Phi-2 on document search quality"""
import os
import time
from llama_cpp import Llama

models = [
    ('TinyLlama', 'models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf'),
    ('Phi-2', 'models/phi-2.Q4_K_M.gguf'),
]

# Simulated document search scenario
test_context = """
[From: Siddhesh_Bhurke_Resume.pdf]
Summary: Siddhesh Bhurke is an experienced Data Analytics Consultant with skills in Python, 
PySpark, SQL, data engineering, and machine learning. He has a substantial record of 
driving revenue growth. Contact: +44-7405332986, bhurke.siddhesh@gmail.com, London UK.
"""

test_question = "What are Siddhesh's skills?"

prompt = f"""You are a document search assistant. Answer using ONLY the provided documents.

Documents:
{test_context}

Question: {test_question}

Answer (cite specific details):"""

print('='*60)
print('MODEL QUALITY COMPARISON - Document Search')
print('='*60)
print(f'Question: {test_question}')
print('='*60)

for name, path in models:
    print(f'\n{name}:')
    try:
        llm = Llama(path, n_ctx=1024, verbose=False)
        start = time.time()
        out = llm(prompt, max_tokens=100, temperature=0.2)
        latency = time.time() - start
        answer = out['choices'][0]['text'].strip()
        print(f'  Latency: {latency:.1f}s')
        print(f'  Answer: {answer[:200]}')
        
        # Quality check: does it mention key skills?
        skills_mentioned = sum(1 for s in ['python', 'sql', 'pyspark', 'data'] if s in answer.lower())
        print(f'  Skills Score: {skills_mentioned}/4 keywords found')
        del llm
    except Exception as e:
        print(f'  ERROR: {e}')

print('\n' + '='*60)
print('RECOMMENDATION:')
print('  Use Phi-2 for better quality (larger model)')
print('  Use TinyLlama for faster responses (smaller model)')
print('='*60)
