"""Quick model diagnostic script"""
import os
from llama_cpp import Llama

models = [
    'models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf',
    'models/phi-2.Q4_K_M.gguf',
    'models/llama-2-7b-chat.Q4_K_M.gguf',
    'models/mistral-7b-instruct-v0.1.Q4_K_M.gguf'
]

print('='*50)
print('MODEL LOADING TEST')
print('='*50)

results = []

for m in models:
    name = os.path.basename(m)
    print(f'\n{name}:')
    try:
        llm = Llama(m, n_ctx=256, verbose=False)
        out = llm('What is 2+2?', max_tokens=10)
        answer = out['choices'][0]['text'].strip()[:50]
        print(f'  STATUS: OK')
        print(f'  OUTPUT: {answer}')
        results.append({'model': name, 'status': 'OK', 'answer': answer})
        del llm
    except Exception as e:
        err = str(e)[:80]
        print(f'  STATUS: FAILED')
        print(f'  ERROR: {err}')
        results.append({'model': name, 'status': 'FAILED', 'error': err})

print('\n' + '='*50)
print('SUMMARY')
print('='*50)
working = [r for r in results if r['status'] == 'OK']
print(f'Working models: {len(working)}/{len(results)}')
for r in results:
    status = 'OK' if r['status'] == 'OK' else 'FAIL'
    print(f"  [{status}] {r['model']}")
