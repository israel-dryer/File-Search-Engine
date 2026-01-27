from typing import List, Dict, Any
from backend import search, database, llm_integration
from backend.file_processing import extract_text
import json
import os

def tool_search_knowledge_base(query: str, global_state: dict) -> str:
    """
    Search the indexed files for information.
    Args:
        query: The search query (e.g., "revenue 2023", "Project Alpha budget")
    """
    if not global_state.get('index'):
        return "Error: No knowledge base indexed."
        
    results, _ = search.search(
        query, 
        global_state['index'], 
        global_state['docs'], 
        global_state['tags'], 
        llm_integration.get_embeddings(global_state['config'].get('LocalLLM', 'provider', fallback='openai')),
        global_state.get('index_summaries'),
        global_state.get('cluster_summaries'),
        global_state.get('cluster_map'),
        global_state.get('bm25')
    )
    
    if not results:
        return "No relevant information found."
        
    # Format results for the agent
    summary = []
    for r in results[:5]:
        meta = r.get('file_name', 'unknown')
        text = r.get('document', '')[:500] # Truncate for token efficiency
        summary.append(f"Source: {meta}\nContent: {text}\n")
        
    return "\n---\n".join(summary)

def tool_read_file(file_path: str) -> str:
    """
    Read the full content of a specific file.
    Args:
        file_path: Absolute or relative path to the file.
    """
    if not file_path:
        return "Error: No file path provided."
        
    resolved_path = file_path
    if not os.path.exists(file_path):
        # Clean the input (remove quotes if any)
        clean_name = file_path.strip("'\" ")
        # Try to find by filename in DB
        file_info = database.get_file_by_name(clean_name)
        if file_info:
            resolved_path = file_info['path']
        else:
             # Try search in CWD just in case
             if os.path.exists(clean_name):
                 resolved_path = clean_name
             else:
                 return f"Error: File '{file_path}' not found. Use 'list_files' to see available files."

    try:
        from backend.file_processing import extract_text
        text = extract_text(resolved_path)
        if not text:
            return "File is empty or could not be read."
        return text[:5000] # Hard limit to prevent context overflow
    except Exception as e:
        return f"Error reading file: {str(e)}"

def tool_list_files(query: str = None) -> str:
    """
    List all available files in the index.
    """
    files = database.get_all_files()
    if not files:
        return "No files indexed."
    return ", ".join([f['filename'] for f in files[:50]]) # Limit to 50

AVAILABLE_TOOLS = {
    "search_knowledge_base": tool_search_knowledge_base,
    "read_file": tool_read_file,
    "list_files": tool_list_files
}
