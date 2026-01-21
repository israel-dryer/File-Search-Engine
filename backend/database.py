import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional

# Path configuration for new folder structure
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)
DATABASE_PATH = os.path.join(DATA_DIR, 'metadata.db')

def get_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize the database schema."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Files table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT UNIQUE NOT NULL,
            filename TEXT NOT NULL,
            extension TEXT,
            size_bytes INTEGER,
            modified_date DATETIME,
            indexed_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            chunk_count INTEGER DEFAULT 0,
            faiss_start_idx INTEGER,
            faiss_end_idx INTEGER
        )
    """)
    
    # Search history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            result_count INTEGER,
            execution_time_ms INTEGER
        )
    """)
    
    # Preferences table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS preferences (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    # Folder history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS folder_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT UNIQUE NOT NULL,
            added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_used_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Populate history from existing files if empty
    cursor.execute("SELECT COUNT(*) FROM folder_history")
    if cursor.fetchone()[0] == 0:
        try:
            cursor.execute("SELECT path FROM files")
            files = cursor.fetchall()
            seen_folders = set()
            timestamp = datetime.now()
            
            for row in files:
                folder = os.path.dirname(row['path'])
                if folder and folder not in seen_folders:
                    seen_folders.add(folder)
                    cursor.execute("INSERT OR IGNORE INTO folder_history (path, added_at, last_used_at) VALUES (?, ?, ?)", 
                                  (folder, timestamp, timestamp))
            if seen_folders:
                print(f"Migrated {len(seen_folders)} folders to history.")
        except Exception as e:
            print(f"Migration failed: {e}")
            
    conn.commit()
    conn.close()

def add_file(path: str, filename: str, extension: str, size_bytes: int, 
             modified_date: datetime, chunk_count: int, 
             faiss_start_idx: int, faiss_end_idx: int) -> int:
    """Add a file to the database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO files 
        (path, filename, extension, size_bytes, modified_date, chunk_count, faiss_start_idx, faiss_end_idx)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (path, filename, extension, size_bytes, modified_date, chunk_count, faiss_start_idx, faiss_end_idx))
    
    file_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return file_id

def get_all_files() -> List[Dict]:
    """Get all indexed files."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM files ORDER BY indexed_date DESC")
    files = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return files

def get_file_by_path(path: str) -> Optional[Dict]:
    """Get a file by its path."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM files WHERE path = ?", (path,))
    row = cursor.fetchone()
    
    conn.close()
    return dict(row) if row else None

def delete_file(file_id: int):
    """Delete a file from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM files WHERE id = ?", (file_id,))
    
    conn.commit()
    conn.close()

def add_search_history(query: str, result_count: int, execution_time_ms: int):
    """Add a search to history."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO search_history (query, result_count, execution_time_ms)
        VALUES (?, ?, ?)
    """, (query, result_count, execution_time_ms))
    
    conn.commit()
    conn.close()

def get_search_history(limit: int = 20) -> List[Dict]:
    """Get recent search history."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM search_history 
        ORDER BY timestamp DESC 
        LIMIT ?
    """, (limit,))
    
    history = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return history

def clear_all_files():
    """Clear all files from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM files")
    
    conn.commit()
    conn.close()

def get_preference(key: str) -> Optional[str]:
    """Get a preference value."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT value FROM preferences WHERE key = ?", (key,))
    row = cursor.fetchone()
    
    conn.close()
    return row['value'] if row else None

def set_preference(key: str, value: str):
    """Set a preference value."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO preferences (key, value)
        VALUES (?, ?)
    """, (key, value))
    
    conn.commit()
    conn.close()

def get_file_by_faiss_index(faiss_idx: int) -> Optional[Dict]:
    """Get the file that contains a specific FAISS chunk index."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM files 
        WHERE faiss_start_idx <= ? AND faiss_end_idx >= ?
    """, (faiss_idx, faiss_idx))
    row = cursor.fetchone()
    
    conn.close()
    return dict(row) if row else None

def delete_search_history_item(history_id: int) -> bool:
    """Delete a single search history item."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM search_history WHERE id = ?", (history_id,))
    deleted = cursor.rowcount > 0
    
    conn.commit()
    conn.close()
    return deleted

def delete_all_search_history() -> int:
    """Delete all search history. Returns count of deleted items."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM search_history")
    count = cursor.fetchone()[0]
    
    cursor.execute("DELETE FROM search_history")
    
    conn.commit()
    conn.close()
    return count

def add_folder_to_history(path: str):
    """Add or update a folder in history."""
    conn = get_connection()
    cursor = conn.cursor()
    
    timestamp = datetime.now()
    
    # Check if exists
    cursor.execute("SELECT id FROM folder_history WHERE path = ?", (path,))
    row = cursor.fetchone()
    
    if row:
        cursor.execute("UPDATE folder_history SET last_used_at = ? WHERE id = ?", (timestamp, row['id']))
    else:
        cursor.execute("INSERT INTO folder_history (path, added_at, last_used_at) VALUES (?, ?, ?)", 
                      (path, timestamp, timestamp))
    
    conn.commit()
    conn.close()

def get_folder_history(limit: int = 20) -> List[Dict]:
    """Get recent folder history."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM folder_history ORDER BY last_used_at DESC LIMIT ?", (limit,))
    history = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return history

def delete_folder_history_item(path: str) -> bool:
    """Delete a single folder from history. Returns True if deleted."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM folder_history WHERE path = ?", (path,))
    deleted = cursor.rowcount > 0
    
    conn.commit()
    conn.close()
    return deleted

def clear_folder_history() -> int:
    """Clear all folder history. Returns count of deleted items."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM folder_history")
    count = cursor.fetchone()[0]
    
    cursor.execute("DELETE FROM folder_history")
    
    conn.commit()
    conn.close()
    return count

# Database initialization moved to api.py startup_event
# to prevent side effects on import (file locking)

