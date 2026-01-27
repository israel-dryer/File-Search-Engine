import os

paths = [
    r"C:\Users\siddh\OneDrive\Desktop\Resume",
    r"C:\Users\siddh\Desktop\Resume"
]

print("Checking paths:")
for p in paths:
    print(f"\nPath: {p}")
    if os.path.exists(p):
        print(f"  Exists: Yes")
        files = []
        for _, _, filenames in os.walk(p):
            files.extend(filenames)
        print(f"  Files found via os.walk: {len(files)}")
        if files:
            print(f"  First 3 files: {files[:3]}")
    else:
        print(f"  Exists: No")
