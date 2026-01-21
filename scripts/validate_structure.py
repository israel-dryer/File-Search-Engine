import os
import sys

# Protocol Definitions
ALLOWED_ROOT_FILES = [
    'package.json', 'package-lock.json', 'README.md', 'AGENTS.md', 
    'config.ini', '.gitignore', 'requirements.txt', 'LICENSE', 'CHANGELOG.md'
]
ALLOWED_ROOT_EXTENSIONS = ['.md', '.json', '.ini', '.txt', '.js', '.png', '.PNG'] # limited JS allow for tailwind.config?
DISALLOWED_ROOT_EXTENSIONS = ['.py']

STRUCTURE_RULES = {
    'backend': {
        'required': True,
        'description': "All Python source code for the application logic."
    },
    'scripts': {
        'required': True,
        'description': "Utility scripts, benchmarks, and tools."
    },
    'data': {
        'required': True,
        'description': "Generated artifacts (DBs, indices, logs)."
    }
}

DATA_EXTENSIONS = ['.db', '.faiss', '.pkl']

def validate_structure():
    """Validate the project folder structure."""
    project_root = os.getcwd()
    errors = []
    warnings = []

    print(f"Validating specific folder structure in: {project_root}")

    # 1. Check Root Directory for Pollution
    for item in os.listdir(project_root):
        if item.startswith('.') or item == 'venv' or item == 'node_modules' or item == '__pycache__':
            continue
            
        full_path = os.path.join(project_root, item)
        
        if os.path.isfile(full_path):
            ext = os.path.splitext(item)[1]
            
            if ext in DISALLOWED_ROOT_EXTENSIONS:
                errors.append(f"ROOT POLLUTION: Found {item} in root. Move to 'backend/' or 'scripts/'.")
            
            if item not in ALLOWED_ROOT_FILES and ext not in ALLOWED_ROOT_EXTENSIONS:
                warnings.append(f"ROOT WARNING: Unexpected file {item} in root.")

        elif os.path.isdir(full_path):
            if item == 'models':
                continue # Allowed
            if item not in STRUCTURE_RULES and item not in ['frontend', 'backend', 'scripts', 'data']:
                warnings.append(f"ROOT WARNING: Unexpected directory '{item}' in root.")

    # 2. Check Data Directory Rule
    if os.path.exists('data'):
        # Good
        pass
    else:
        # data directory might be created at runtime, but warn if missing
        warnings.append("MISSING DIRECTORY: 'data/' directory should exist for generated files.")
        
    # Check if data files are leaking elsewhere
    for root, dirs, files in os.walk(project_root):
        if 'venv' in root or 'node_modules' in root or 'tests' in root or '.git' in root or 'data' in root:
            continue
            
        for file in files:
            ext = os.path.splitext(file)[1]
            if ext in DATA_EXTENSIONS:
                # relative path
                rel_path = os.path.relpath(os.path.join(root, file), project_root)
                errors.append(f"DATA LEAK: Found data file '{rel_path}' outside 'data/' directory.")

    # Report
    print("\n--- Validation Report ---")
    if warnings:
        for w in warnings:
            print(f"[WARN] {w}")
            
    if errors:
        for e in errors:
            print(f"[FAIL] {e}")
        print("\nSTRUCTURE VALIDATION FAILED")
        sys.exit(1)
    else:
        print("\nSTRUCTURE VALIDATION PASSED ✓")
        sys.exit(0)

if __name__ == "__main__":
    validate_structure()
