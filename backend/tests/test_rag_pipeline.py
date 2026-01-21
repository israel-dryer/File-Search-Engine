import configparser
import os
import sys
from backend.llm_integration import generate_ai_answer

# Read config
config = configparser.ConfigParser()
config.read('config.ini')

model_path = config.get('LocalLLM', 'model_path', fallback=None)
print(f"Model path from config: {model_path}")

if not model_path or not os.path.exists(model_path):
    print("Invalid model path in config!")
    # Try to find one manually for testing
    if os.path.exists("models"):
        files = os.listdir("models")
        if files:
            model_path = os.path.join("models", files[0])
            print(f"Fallback to: {model_path}")

context = """
Siddhesh Bhurke - Data Analyst
Education:
MBA in Data Science from Symbiosis Centre for Information Technology (2021-2023).
PG Diploma from Welingkar Institute.
"""

question = "where did siddhesh study?"

print("-" * 20)
print(f"Context: {context}")
print(f"Question: {question}")
print(f"Model: {model_path}")
print("-" * 20)

if model_path:
    print("Calling generate_ai_answer...")
    try:
        answer = generate_ai_answer(context, question, model_path)
        print(f"Result: '{answer}'")
    except Exception as e:
        print(f"Error: {e}")
else:
    print("No model path available to test.")
