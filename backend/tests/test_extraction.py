# Test script to verify indexing works
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.file_processing import extract_text

# Test folder
test_folder = r'C:\Users\siddh\OneDrive\Desktop\Resume'

print(f"Testing file extraction from: {test_folder}")
print("="*60)

if not os.path.exists(test_folder):
    print(f"ERROR: Folder does not exist: {test_folder}")
    sys.exit(1)

# List all files
all_files = []
for dirpath, _, filenames in os.walk(test_folder):
    for filename in filenames:
        filepath = os.path.join(dirpath, filename)
        all_files.append(filepath)

print(f"Found {len(all_files)} files:")
for i, filepath in enumerate(all_files, 1):
    print(f"  {i}. {os.path.basename(filepath)} ({os.path.splitext(filepath)[1]})")

print("\n" + "="*60)
print("Testing text extraction...")
print("="*60 + "\n")

successful = 0
failed = 0

for filepath in all_files:
    filename = os.path.basename(filepath)
    ext = os.path.splitext(filepath)[1].lower()
    
    try:
        text = extract_text(filepath)
        if text:
            text_preview = text[:200].replace('\n', ' ')
            print(f"✓ {filename}: {len(text)} chars - \"{text_preview}...\"")
            successful += 1
        else:
            print(f"✗ {filename}: No text extracted")
            failed += 1
    except Exception as e:
        print(f"✗ {filename}: Error - {e}")
        failed += 1

print("\n" + "="*60)
print(f"Results: {successful} successful, {failed} failed")
print("="*60)
