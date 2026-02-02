## 2024-05-22 - [Critical] Arbitrary File Deletion in Model Manager
**Vulnerability:** The `delete_model` function in `backend/model_manager.py` accepted an absolute file path from the user and passed it directly to `os.remove()` without validation. This allowed attackers to delete any file on the system that the process had permissions to access (Arbitrary File Deletion).
**Learning:** Never trust file paths provided by users, even in internal-facing APIs. Relying on the frontend to provide "safe" paths is insufficient. Always validate that a file path resides within the expected directory on the server side using `os.path.commonpath`.
**Prevention:** Implement a strict `is_safe_path` helper that resolves paths to their absolute form and checks containment within a trusted base directory before performing any file operations.

## 2026-02-01 - [Arbitrary File Deletion in Model Manager]
**Vulnerability:** The `delete_model` function in `backend/model_manager.py` accepted an absolute file path directly from the API request and passed it to `os.remove` without validation. This allowed an attacker to delete any file on the system (e.g., `/etc/passwd`) by providing its path.
**Learning:** The vulnerability existed because the API endpoint relied on the frontend to provide the correct path, assuming good intent. The tests (`test_model_manager.py`) verified other aspects of the module but completely missed the `delete_model` function, leaving the vulnerability exposed.
**Prevention:** Always validate file paths against a whitelist or a base directory using `os.path.commonpath` (wrapped in a `is_safe_path` helper). Never trust file paths from user input. Ensure unit tests cover all public functions, especially those performing destructive actions like deletion.
