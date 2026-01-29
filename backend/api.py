from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
import json
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os
import time
import configparser

# Path configuration for new folder structure
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
CONFIG_PATH = os.path.join(BASE_DIR, 'config.ini')
INDEX_PATH = os.path.join(DATA_DIR, 'index.faiss')
BENCHMARK_PATH = os.path.join(DATA_DIR, 'benchmark_results.json')
LOG_PATH = os.path.join(DATA_DIR, 'app.log')

# Configure logging FIRST
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
logger.info("--- SERVER RESTARTING (Logging Configured Early) ---")

# --- Lazy Loading Helpers ---
# These functions allow us to defer heavy imports while keeping tests patchable at the module level

def get_embeddings(*args, **kwargs):
    from backend.llm_integration import get_embeddings as _get_embeddings
    return _get_embeddings(*args, **kwargs)

def summarize(*args, **kwargs):
    from backend.llm_integration import summarize as _summarize
    return _summarize(*args, **kwargs)

def search(*args, **kwargs):
    from backend.search import search as _search
    return _search(*args, **kwargs)

def create_index(*args, **kwargs):
    from backend.indexing import create_index as _create_index
    return _create_index(*args, **kwargs)

def save_index(*args, **kwargs):
    from backend.indexing import save_index as _save_index
    return _save_index(*args, **kwargs)

def load_index(*args, **kwargs):
    from backend.indexing import load_index as _load_index
    return _load_index(*args, **kwargs)

def smart_summary(*args, **kwargs):
    from backend.llm_integration import smart_summary as _smart_summary
    return _smart_summary(*args, **kwargs)

def cached_smart_summary(*args, **kwargs):
    from backend.llm_integration import cached_smart_summary as _cached_smart_summary
    return _cached_smart_summary(*args, **kwargs)

def cached_generate_ai_answer(*args, **kwargs):
    from backend.llm_integration import cached_generate_ai_answer as _cached_generate_ai_answer
    return _cached_generate_ai_answer(*args, **kwargs)

def stream_ai_answer(*args, **kwargs):
    from backend.llm_integration import stream_ai_answer as _stream_ai_answer
    return _stream_ai_answer(*args, **kwargs)

def get_available_models(*args, **kwargs):
    from backend.model_manager import get_available_models as _get_available_models
    return _get_available_models(*args, **kwargs)

def get_local_models(*args, **kwargs):
    from backend.model_manager import get_local_models as _get_local_models
    return _get_local_models(*args, **kwargs)

def start_download(*args, **kwargs):
    from backend.model_manager import start_download as _start_download
    return _start_download(*args, **kwargs)

def get_download_status(*args, **kwargs):
    from backend.model_manager import get_download_status as _get_download_status
    return _get_download_status(*args, **kwargs)

# -----------------------------
from backend import database



app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:5175", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
index = None
docs = []
tags = []
index_summaries = None
cluster_summaries = []
cluster_map = None
bm25 = None

@app.get("/")
async def root():
    return {"status": "online", "message": "File Search Engine API is running"}

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

def load_config():
    import configparser
    if not os.path.exists(CONFIG_PATH):
        config = configparser.ConfigParser()
        config['General'] = {'folder': '', 'auto_index': 'False'}
        config['APIKeys'] = {'openai_api_key': ''}
        config['LocalLLM'] = {'model_path': '', 'provider': 'openai'}
        with open(CONFIG_PATH, 'w') as configfile:
            config.write(configfile)
    
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    return config

def save_config_file(config):
    with open(CONFIG_PATH, 'w') as configfile:
        config.write(configfile)

# Initialize index on startup if available
@app.on_event("startup")
async def startup_event():
    logger.info("Application starting up...")
    database.init_database()
    # Load index in background to not block health checks
    asyncio.create_task(load_initial_index())

async def load_initial_index():
    global index, docs, tags, index_summaries, cluster_summaries, cluster_map, bm25
    if os.path.exists(INDEX_PATH):
        try:
            # load_index is a blocking call, run it in a thread
            logger.info("Loading existing index in background...")
            res = await asyncio.to_thread(load_index, INDEX_PATH)
            index, docs, tags, index_summaries, cluster_summaries, cluster_map, bm25 = res
            logger.info("Loaded existing index successfully.")
        except Exception as e:
            logger.error(f"Error loading index: {e}")
            index = None
            docs = []
            tags = []
            index_summaries = None
            cluster_summaries = []
            cluster_map = None
            bm25 = None

@app.get("/api/browse")
async def browse_folder():
    """Open a folder browser dialog and return the selected path."""
    import tkinter as tk
    from tkinter import filedialog
    try:
        # Create a hidden root window
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)  # Bring dialog to front
        
        folder_path = filedialog.askdirectory(title="Select Folder to Index")
        root.destroy()
        
        if folder_path:
            return {"folder": folder_path}
        else:
            return {"folder": None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to open folder dialog: {str(e)}")

@app.get("/api/models/available")
async def list_available_models():
    return get_available_models()

@app.get("/api/models/local")
async def list_local_models():
    return get_local_models()

@app.post("/api/models/download/{model_id}")
async def download_model_endpoint(model_id: str):
    success, message = start_download(model_id)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"status": "success", "message": message}

@app.get("/api/models/status")
async def download_status_endpoint():
    return get_download_status()

@app.delete("/api/models/delete")
async def delete_model(request: dict):
    """Delete a downloaded model file."""
    model_path = request.get('path', '')
    if not model_path:
        raise HTTPException(status_code=400, detail="Model path required")
    
    try:
        from backend.model_manager import delete_model
        if delete_model(model_path):
            return {"status": "success", "message": "Model deleted"}
        else:
            raise HTTPException(status_code=404, detail="Model file not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Benchmark state
benchmark_status = {
    "running": False,
    "progress": 0,
    "current_model": None,
    "error": None
}
benchmark_results = None

# Indexing state
indexing_status = {
    "running": False,
    "progress": 0,
    "current_file": None,
    "total_files": 0,
    "processed_files": 0,
    "error": None
}

def run_benchmark_task():
    """Background task to run benchmarks."""
    global benchmark_status, benchmark_results
    import json
    
    try:
        benchmark_status["running"] = True
        benchmark_status["progress"] = 0
        benchmark_status["error"] = None
        
        # Import and run benchmarks
        from scripts.benchmark_models import run_all_benchmarks, save_results
        
        results = run_all_benchmarks(verbose=False)
        if results:
            save_results(results)
            benchmark_results = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "results": [r.to_dict() for r in results]
            }
        
        benchmark_status["running"] = False
        benchmark_status["progress"] = 100
        
    except Exception as e:
        benchmark_status["running"] = False
        benchmark_status["error"] = str(e)

@app.post("/api/benchmarks/run")
async def run_benchmarks(background_tasks: BackgroundTasks):
    """Start benchmark suite in background."""
    global benchmark_status
    
    if benchmark_status["running"]:
        raise HTTPException(status_code=400, detail="Benchmark already running")
    
    background_tasks.add_task(run_benchmark_task)
    return {"status": "started", "message": "Benchmark started in background"}

@app.get("/api/benchmarks/status")
async def get_benchmark_status():
    """Get current benchmark status."""
    return benchmark_status

@app.get("/api/benchmarks/results")
async def get_benchmark_results():
    """Get latest benchmark results."""
    global benchmark_results
    
    # Try to load from file if not in memory
    if benchmark_results is None:
        if os.path.exists(BENCHMARK_PATH):
            import json
            with open(BENCHMARK_PATH, 'r') as f:
                benchmark_results = json.load(f)
    
    if benchmark_results is None:
        return {"results": [], "message": "No benchmark results available. Run a benchmark first."}
    
    return benchmark_results




class SearchRequest(BaseModel):
    query: str

class SearchResult(BaseModel):
    document: str
    summary: Optional[str] = None
    tags: List[str] = []
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    faiss_idx: Optional[int] = None

class SearchResponse(BaseModel):
    results: List[SearchResult]
    ai_answer: Optional[str] = ""
    active_model: Optional[str] = ""

class ConfigModel(BaseModel):
    folders: List[str] = []
    auto_index: bool = False
    openai_api_key: Optional[str] = ""
    gemini_api_key: Optional[str] = ""
    anthropic_api_key: Optional[str] = ""
    grok_api_key: Optional[str] = ""
    local_model_path: Optional[str] = ""
    provider: str = "openai"
    tensor_split: Optional[str] = None

@app.get("/api/config")
async def get_config():
    config = load_config()
    # Handle both old 'folder' and new 'folders' format
    folder = config.get('General', 'folder', fallback='')
    folders_str = config.get('General', 'folders', fallback='')
    
    folders = [f.strip() for f in folders_str.split(',') if f.strip()]
    if not folders and folder:
        folders = [folder]
        
    return {
        "folders": folders,
        "auto_index": config.getboolean('General', 'auto_index', fallback=False),
        "openai_api_key": config.get('APIKeys', 'openai_api_key', fallback=''),
        "gemini_api_key": config.get('APIKeys', 'gemini_api_key', fallback=''),
        "anthropic_api_key": config.get('APIKeys', 'anthropic_api_key', fallback=''),
        "grok_api_key": config.get('APIKeys', 'grok_api_key', fallback=''),
        "local_model_path": config.get('LocalLLM', 'model_path', fallback=''),
        "provider": config.get('LocalLLM', 'provider', fallback='openai'),
        "tensor_split": config.get('LocalLLM', 'tensor_split', fallback=None)
    }

@app.post("/api/config")
async def update_config(config_data: ConfigModel):
    config = configparser.ConfigParser()
    config['General'] = {
        'folders': ','.join(config_data.folders),
        'auto_index': str(config_data.auto_index)
    }
    config['APIKeys'] = {
        'openai_api_key': config_data.openai_api_key or '',
        'gemini_api_key': config_data.gemini_api_key or '',
        'anthropic_api_key': config_data.anthropic_api_key or '',
        'grok_api_key': config_data.grok_api_key or ''
    }
    config['LocalLLM'] = {
        'model_path': config_data.local_model_path or '', 
        'provider': config_data.provider,
        'tensor_split': config_data.tensor_split or ''
    }
    save_config_file(config)
    
    # Save folders to history
    try:
        if config_data.folders:
            for folder in config_data.folders:
                database.add_folder_to_history(folder)
    except Exception as e:
        print(f"Failed to update folder history: {e}")
        
    return {"status": "success", "message": "Configuration saved"}

@app.post("/api/search")
async def search_files(request: SearchRequest):
    global index, docs, tags, index_summaries, cluster_summaries, cluster_map, bm25
    
    if not index:
        raise HTTPException(status_code=400, detail="Index not loaded. Please configure and index a folder first.")

    print(f"\n[API] POST /api/search - Query: '{request.query}'")

    try:
        start_time = time.time()
        
        config = load_config()
        provider = config.get('LocalLLM', 'provider', fallback='openai')
        
        # Determine correct API key based on provider
        api_key = config.get('APIKeys', 'openai_api_key', fallback=None)
        if provider == 'gemini':
            api_key = config.get('APIKeys', 'gemini_api_key', fallback=api_key)
        elif provider == 'anthropic':
            api_key = config.get('APIKeys', 'anthropic_api_key', fallback=api_key)
        elif provider == 'grok':
            api_key = config.get('APIKeys', 'grok_api_key', fallback=api_key)

        is_agentic = config.get('General', 'agent_mode', fallback='False').lower() == 'true'
        
        if is_agentic:
            print("[API] Running in AGENTIC mode.")
            from backend.agent import ReActAgent
            agent = ReActAgent(provider, api_key, {
                'index': index, 'docs': docs, 'tags': tags, 'config': config,
                'index_summaries': index_summaries, 'cluster_summaries': cluster_summaries,
                'cluster_map': cluster_map, 'bm25': bm25
            })
            return StreamingResponse(agent.stream_chat(request.query), media_type="text/event-stream")

        model_path = config.get('LocalLLM', 'model_path', fallback=None)
        tensor_split_str = config.get('LocalLLM', 'tensor_split', fallback=None)
        tensor_split = None
        if tensor_split_str:
            try:
                tensor_split = [float(x) for x in tensor_split_str.split(',')]
            except:
                pass

        # Run Search
        results, context_snippets = search(
            request.query, index, docs, tags, 
            get_embeddings(provider, api_key, model_path),
            index_summaries, cluster_summaries, cluster_map, bm25
        )
        
        processed_results = []
        
        # Helper to get full file path
        # Note: search() now returns a list of result dicts directly
        # We need to adapt the caching logic below
        
        # Wait, the previous logic was:
        # results = search(...) -> returns list of dicts
        for idx, result in enumerate(results):
            faiss_idx = result.get('faiss_idx')
            
            # Use file info from search result first (it comes from FAISS doc metadata)
            # Only fall back to database lookup if not available
            file_path = result.get('file_path')
            file_name = result.get('file_name')
            
            # If not in search result, try database lookup (for backward compatibility)
            if not file_path and faiss_idx is not None:
                file_info = database.get_file_by_faiss_index(faiss_idx)
                if file_info:
                    file_path = file_info.get('path')
                    file_name = file_info.get('filename')
            
            # OPTIMIZATION: Use fast summary for all results to avoid blocking
            summary = summarize(result['document'], provider, api_key, model_path, question=request.query)
            
            # Add file context to snippets for AI answer
            file_prefix = f"[From: {file_name}] " if file_name else ""
            # Format context for AI (Nexus Insight)
            # We prefer using the smart summary if available, otherwise raw document text
            if summary and len(summary) > 20:
                context_snippets.append(f"{file_prefix}{summary}")
            else:
                context_snippets.append(f"{file_prefix}{result['document'][:500]}")

            # Convert tags from string to list if needed
            result_tags = result.get('tags', '')
            if isinstance(result_tags, str):
                result_tags = [t.strip() for t in result_tags.split(',') if t.strip()]
            
            processed_results.append(SearchResult(
                document=result['document'],
                summary=summary,
                tags=result_tags,
                faiss_idx=faiss_idx,
                file_path=file_path,
                file_name=file_name
            ))
        
        # Return results immediately - AI Answer will be streamed via separate endpoint
        active_model_name = provider.capitalize()
        if provider == 'local' and model_path:
            active_model_name = os.path.basename(model_path).replace(".gguf", "").replace("-", " ")
        
        # Save to search history
        execution_time_ms = int((time.time() - start_time) * 1000)
        database.add_search_history(request.query, len(processed_results), execution_time_ms)
            
        return SearchResponse(
            results=processed_results,
            ai_answer="", # Empty for immediate return
            active_model=active_model_name
        )
    except Exception as e:
        logger.error(f"Search error: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/stream-answer")
async def stream_answer_endpoint(request: SearchRequest):
    """
    Stream the AI answer for a given query.
    Re-runs the search to get context (fast) and then streams tokens.
    """
    global index, docs, tags, index_summaries, cluster_summaries, cluster_map, bm25

    if not index:
         return StreamingResponse(iter(["Error: Index not loaded."]), media_type="text/event-stream")

    config = load_config()
    provider = config.get('LocalLLM', 'provider', fallback='openai')
    api_key = config.get('APIKeys', 'openai_api_key', fallback=None)
    if provider == 'gemini':
        api_key = config.get('APIKeys', 'gemini_api_key', fallback=api_key)
    elif provider == 'anthropic':
        api_key = config.get('APIKeys', 'anthropic_api_key', fallback=api_key)
    elif provider == 'grok':
        api_key = config.get('APIKeys', 'grok_api_key', fallback=api_key)

    model_path = config.get('LocalLLM', 'model_path', fallback=None)
    tensor_split_str = config.get('LocalLLM', 'tensor_split', fallback=None)
    tensor_split = None
    if tensor_split_str:
        try:
            tensor_split = [float(x) for x in tensor_split_str.split(',')]
        except:
            pass

    # Re-run search to get context
    results, context_snippets = search(
        request.query, index, docs, tags,
        get_embeddings(provider, api_key, model_path),
        index_summaries, cluster_summaries, cluster_map, bm25
    )

    # Prepare context
    final_context_snippets = []
    for idx, result in enumerate(results):
         # Use fast fallback summary for streaming context (no new LLM calls)
         summary = summarize(result['document'], provider, api_key, model_path, question=request.query)
         file_name = result.get('file_name', '')
         file_prefix = f"[From: {file_name}] " if file_name else ""
         if summary and len(summary) > 20:
             final_context_snippets.append(f"{file_prefix}{summary}")
         else:
             final_context_snippets.append(f"{file_prefix}{result['document'][:500]}")

    safe_snippets = [s[:600] for s in final_context_snippets[:6]]
    context_text = "\n\n".join(safe_snippets)

    if not context_text:
        return StreamingResponse(iter(["No relevant context found."]), media_type="text/event-stream")

    async def generate():
        for token in stream_ai_answer(context_text, request.query, provider, api_key, model_path, tensor_split):
            yield token

    return StreamingResponse(generate(), media_type="text/event-stream")

@app.get("/api/search/history")
async def get_search_history():
    """Get recent search history."""
    try:
        history = database.get_search_history(limit=50)
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/search/history/{history_id}")
async def delete_search_history_item(history_id: int):
    """Delete a single search history item."""
    try:
        success = database.delete_search_history_item(history_id)
        if success:
            return {"status": "success", "message": "History item deleted"}
        raise HTTPException(status_code=404, detail="History item not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/search/history")
async def delete_all_search_history():
    """Delete all search history."""
    try:
        count = database.delete_all_search_history()
        return {"status": "success", "message": f"Deleted {count} history items", "deleted_count": count}
    except Exception as e:
        logger.error(f"Error clearing history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class LogRequest(BaseModel):
    level: str
    message: str
    source: Optional[str] = "Frontend"
    stack: Optional[str] = None

@app.post("/api/logs")
async def receive_log(log: LogRequest):
    """endpoint to receive logs from frontend"""
    log_msg = f"[{log.source}] {log.message}"
    if log.stack:
        log_msg += f"\nStack: {log.stack}"
    
    if log.level.lower() == 'error':
        logger.error(log_msg)
    elif log.level.lower() == 'warn' or log.level.lower() == 'warning':
        logger.warning(log_msg)
    else:
        logger.info(log_msg)
    return {"status": "logged"}

@app.post("/api/open-file")
async def open_file(request: dict):
    """Open a file in the default system application."""
    file_path = request.get('path', '')
    if not file_path:
        raise HTTPException(status_code=400, detail="File path is required")
    
    # Normalize path - fix mixed slashes from FAISS metadata
    file_path = os.path.normpath(file_path)
    
    # Security: Only allow opening files that are in the index
    # This prevents opening arbitrary files on the system
    if not database.get_file_by_path(file_path):
        logger.warning(f"Security: Attempt to open non-indexed file: {file_path}")
        raise HTTPException(status_code=403, detail="Access denied: File is not in the index")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")

    try:
        import subprocess
        import platform
        
        if platform.system() == 'Windows':
            os.startfile(file_path)
        elif platform.system() == 'Darwin':  # macOS
            subprocess.run(['open', file_path])
        else:  # Linux
            subprocess.run(['xdg-open', file_path])
        
        return {"status": "success", "message": f"Opened {os.path.basename(file_path)}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to open file: {str(e)}")

@app.get("/api/files")
async def list_indexed_files():
    """Get all indexed files with metadata."""
    try:
        files = database.get_all_files()
        return files
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/folders/history")
async def get_folder_history():
    """Get previously used folders."""
    try:
        # User requested: ONLY show 100% indexed folders in history
        history = database.get_folder_history(indexed_only=True)
        return [item['path'] for item in history]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/folders/history")
async def clear_folder_history():
    """Clear all folder history."""
    try:
        count = database.clear_folder_history()
        return {"status": "success", "message": f"Cleared {count} folder history items", "deleted_count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/folders/history/item")
async def delete_folder_history_item(request: dict):
    """Delete a single folder from history."""
    path = request.get('path', '')
    if not path:
        raise HTTPException(status_code=400, detail="Path is required")
    
    try:
        success = database.delete_folder_history_item(path)
        if success:
            return {"status": "success", "message": "Folder removed from history"}
        raise HTTPException(status_code=404, detail="Folder not found in history")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/validate-path")
async def validate_path(request: dict):
    """Validate a folder path and count indexable files."""
    path = request.get('path', '')
    if not path:
        return {"valid": False, "error": "Path is required"}
    
    if not os.path.exists(path):
        return {"valid": False, "error": "Path does not exist"}
    
    if not os.path.isdir(path):
        return {"valid": False, "error": "Path is not a directory"}
    
    # Count supported files
    supported_extensions = {'.txt', '.pdf', '.docx', '.xlsx', '.pptx'}
    file_count = 0
    for dirpath, _, filenames in os.walk(path):
        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()
            if ext in supported_extensions:
                file_count += 1
    
    return {"valid": True, "file_count": file_count}

@app.get("/api/index/status")
async def get_indexing_status():
    """Get current indexing status."""
    return indexing_status

@app.post("/api/index")
async def trigger_indexing(background_tasks: BackgroundTasks):
    global indexing_status
    if indexing_status["running"]:
        raise HTTPException(status_code=400, detail="Indexing already in progress")
        
    config = load_config()
    folders_str = config.get('General', 'folders', fallback='')
    folders = [f.strip() for f in folders_str.split(',') if f.strip()]
    
    if not folders:
        # Fallback to old single folder
        folder = config.get('General', 'folder', fallback='')
        if folder:
            folders = [folder]
            
    if not folders:
        raise HTTPException(status_code=400, detail="No folders configured for indexing")
    
    # Initialize status
    indexing_status = {
        "running": True,
        "progress": 0,
        "current_file": "Scanning folders...",
        "total_files": 0,
        "processed_files": 0,
        "error": None
    }
    
    background_tasks.add_task(run_indexing, config, folders)
    return {"status": "accepted", "message": "Indexing started in background"}

def indexing_progress_callback(current, total, message=None):
    global indexing_status
    if message:
        indexing_status["current_file"] = message # Reuse current_file field for generic status message
    elif filename := message: # Fallback if called with old signature (unlikely)
        indexing_status["current_file"] = f"Processing {filename}"
        
    indexing_status["processed_files"] = current
    indexing_status["total_files"] = total
    # If 0-100 scale is passed directly as current, respect it
    if total == 100 and current > 1: 
        indexing_status["progress"] = current
    else:
        indexing_status["progress"] = int((current / total) * 100)
    
    # Debug log
    if indexing_status["progress"] % 10 == 0 or message:
        logger.info(f"Indexing Progress: {indexing_status['progress']}% - {indexing_status['current_file']}")

@app.get("/api/agent/chat")
async def agent_chat(query: str):
    """
    Stream agent thoughts and final answer.
    """
    global index, docs, tags, index_summaries, cluster_summaries, cluster_map
    
    # Check index
    if not index:
        # We can't use HTTPException in streaming response easily, yield error
        async def yield_error():
             yield f"data: {json.dumps({'type': 'error', 'content': 'Index not loaded'})}\n\n"
        return StreamingResponse(yield_error(), media_type="text/event-stream")

    # Construct global state for the agent
    config = load_config()
    global_state = {
        'index': index,
        'docs': docs,
        'tags': tags,
        'index_summaries': index_summaries,
        'cluster_summaries': cluster_summaries,
        'cluster_map': cluster_map,
        'bm25': bm25,
        'config': config
    }
    
    from backend.agent import ReActAgent
    agent = ReActAgent(global_state)
    
    async def event_generator():
        try:
            async for event in agent.stream_chat(query):
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")

def run_indexing(config, folders):
    global index, docs, tags, index_summaries, cluster_summaries, cluster_map, bm25, indexing_status
    
    provider = config.get('LocalLLM', 'provider', fallback='openai')
    api_key = config.get('APIKeys', 'openai_api_key', fallback=None)
    model_path = config.get('LocalLLM', 'model_path', fallback=None)
    
    try:
        logger.info(f"Starting indexing for folders: {folders}")
        # Unpack 7 values
        new_index, new_docs, new_tags, new_summ_index, new_summ_docs, new_cluster_map, new_bm25 = create_index(
            folders, provider, api_key, model_path, 
            progress_callback=indexing_progress_callback
        )
        if new_index:
            save_index(new_index, new_docs, new_tags, INDEX_PATH, new_summ_index, new_summ_docs, new_cluster_map, new_bm25)
            index, docs, tags = new_index, new_docs, new_tags
            index_summaries, cluster_summaries, cluster_map = new_summ_index, new_summ_docs, new_cluster_map
            bm25 = new_bm25
            
            logger.info("Indexing completed successfully.")
            indexing_status["running"] = False
            indexing_status["progress"] = 100
            indexing_status["progress"] = 100
            indexing_status["current_file"] = "Complete"
            
            # Mark folders as successfully indexed for history
            for folder in folders:
                database.mark_folder_indexed(folder)
        else:
            logger.error("Indexing failed or no documents found.")
            indexing_status["running"] = False
            indexing_status["error"] = "No documents found or processed"
    except Exception as e:
        logger.error(f"Error during indexing: {e}")
        indexing_status["running"] = False
        indexing_status["error"] = str(e)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)