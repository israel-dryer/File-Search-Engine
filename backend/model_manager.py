import os
import requests
import threading
import shutil
import psutil

# Path configuration for new folder structure
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, 'models')
os.makedirs(MODELS_DIR, exist_ok=True)

# Expanded list of GGUF models with metadata
AVAILABLE_MODELS = [
    # Small Models (< 2GB) - Good for testing and low-resource systems
    {
        "id": "tinyllama-1.1b-chat-v1.0.Q4_K_M",
        "name": "TinyLlama 1.1B Chat",
        "description": "Fast and lightweight, great for older hardware.",
        "size": "637 MB",
        "size_bytes": 668000000,
        "ram_required": 2,
        "category": "small",
        "quantization": "Q4_K_M",
        "use_case": "Quick responses, testing",
        "recommended": True,
        "url": "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
    },
    {
        "id": "stablelm-2-zephyr-1_6b.Q4_K_M",
        "name": "StableLM 2 Zephyr 1.6B",
        "description": "Stability AI's efficient small model.",
        "size": "986 MB",
        "size_bytes": 1034000000,
        "ram_required": 3,
        "category": "small",
        "quantization": "Q4_K_M",
        "use_case": "Chat, general tasks",
        "recommended": False,
        "url": "https://huggingface.co/TheBloke/stablelm-2-zephyr-1_6b-GGUF/resolve/main/stablelm-2-zephyr-1_6b.Q4_K_M.gguf"
    },
    {
        "id": "gemma-2b-it.Q4_K_M",
        "name": "Gemma 2B Instruct (Google)",
        "description": "Google's efficient instruction-tuned model.",
        "size": "1.5 GB",
        "size_bytes": 1600000000,
        "ram_required": 4,
        "category": "small",
        "quantization": "Q4_K_M",
        "use_case": "Instructions, summarization",
        "recommended": True,
        "url": "https://huggingface.co/lmstudio-ai/gemma-2b-it-GGUF/resolve/main/gemma-2b-it-q4_k_m.gguf"
    },
    
    # Medium Models (2-4GB) - Balanced performance
    {
        "id": "phi-2.Q4_K_M",
        "name": "Phi-2 2.7B (Microsoft)",
        "description": "Microsoft's powerful small model with excellent reasoning.",
        "size": "1.7 GB",
        "size_bytes": 1800000000,
        "ram_required": 5,
        "category": "medium",
        "quantization": "Q4_K_M",
        "use_case": "Reasoning, code, math",
        "recommended": True,
        "url": "https://huggingface.co/TheBloke/phi-2-GGUF/resolve/main/phi-2.Q4_K_M.gguf"
    },
    {
        "id": "phi-3-mini-4k-instruct.Q4_K_M",
        "name": "Phi-3 Mini 4K (Microsoft)",
        "description": "Latest Microsoft small model with improved capabilities.",
        "size": "2.2 GB",
        "size_bytes": 2360000000,
        "ram_required": 6,
        "category": "medium",
        "quantization": "Q4_K_M",
        "use_case": "General, reasoning, code",
        "recommended": True,
        "url": "https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf"
    },
    {
        "id": "orca-mini-3b.Q4_K_M",
        "name": "Orca Mini 3B",
        "description": "Microsoft research model, good at following instructions.",
        "size": "1.9 GB",
        "size_bytes": 2040000000,
        "ram_required": 5,
        "category": "medium",
        "quantization": "Q4_K_M",
        "use_case": "Instructions, reasoning",
        "recommended": False,
        "url": "https://huggingface.co/TheBloke/orca_mini_3B-GGUF/resolve/main/orca_mini_3b.Q4_K_M.gguf"
    },
    {
        "id": "rocket-3b.Q4_K_M",
        "name": "Rocket 3B",
        "description": "Fast 3B model optimized for chat.",
        "size": "1.8 GB",
        "size_bytes": 1930000000,
        "ram_required": 5,
        "category": "medium",
        "quantization": "Q4_K_M",
        "use_case": "Chat, fast responses",
        "recommended": False,
        "url": "https://huggingface.co/TheBloke/rocket-3B-GGUF/resolve/main/rocket-3b.Q4_K_M.gguf"
    },
    
    # Large Models (4-8GB) - High quality, needs more RAM
    {
        "id": "mistral-7b-instruct-v0.2.Q4_K_M",
        "name": "Mistral 7B Instruct v0.2",
        "description": "Excellent 7B model with strong performance.",
        "size": "4.37 GB",
        "size_bytes": 4690000000,
        "ram_required": 8,
        "category": "large",
        "quantization": "Q4_K_M",
        "use_case": "General, summarization, chat",
        "recommended": True,
        "url": "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
    },
    {
        "id": "llama-2-7b-chat.Q4_K_M",
        "name": "Llama 2 7B Chat (Meta)",
        "description": "Meta's popular open-source chat model.",
        "size": "4.08 GB",
        "size_bytes": 4380000000,
        "ram_required": 8,
        "category": "large",
        "quantization": "Q4_K_M",
        "use_case": "Chat, general tasks",
        "recommended": False,
        "url": "https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q4_K_M.gguf"
    },
    {
        "id": "qwen1.5-7b-chat.Q4_K_M",
        "name": "Qwen 1.5 7B Chat (Alibaba)",
        "description": "Alibaba's multilingual chat model.",
        "size": "4.4 GB",
        "size_bytes": 4720000000,
        "ram_required": 8,
        "category": "large",
        "quantization": "Q4_K_M",
        "use_case": "Multilingual, chat",
        "recommended": False,
        "url": "https://huggingface.co/Qwen/Qwen1.5-7B-Chat-GGUF/resolve/main/qwen1_5-7b-chat-q4_k_m.gguf"
    },
    {
        "id": "zephyr-7b-beta.Q4_K_M",
        "name": "Zephyr 7B Beta",
        "description": "HuggingFace's helpful assistant model.",
        "size": "4.37 GB",
        "size_bytes": 4690000000,
        "ram_required": 8,
        "category": "large",
        "quantization": "Q4_K_M",
        "use_case": "Helpful assistant, chat",
        "recommended": False,
        "url": "https://huggingface.co/TheBloke/zephyr-7B-beta-GGUF/resolve/main/zephyr-7b-beta.Q4_K_M.gguf"
    },
    # High-Quality / Latest Models
    {
        "id": "Meta-Llama-3-8B-Instruct.Q4_K_M",
        "name": "Llama 3 8B Instruct",
        "description": "Meta's latest high-performance 8B model. Excellent for summarization.",
        "size": "4.92 GB",
        "size_bytes": 5280000000,
        "ram_required": 10,
        "category": "large",
        "quantization": "Q4_K_M",
        "use_case": "Advanced Summarization, Chat, Reasoning",
        "recommended": True,
        "url": "https://huggingface.co/MaziyarPanahi/Meta-Llama-3-8B-Instruct-GGUF/resolve/main/Meta-Llama-3-8B-Instruct.Q4_K_M.gguf"
    },
    {
        "id": "Phi-3.5-mini-instruct.Q4_K_M",
        "name": "Phi-3.5 Mini Instruct",
        "description": "Microsoft's latest state-of-the-art small model (3.8B). Extremely capable.",
        "size": "2.4 GB",
        "size_bytes": 2500000000,
        "ram_required": 6,
        "category": "medium",
        "quantization": "Q4_K_M",
        "use_case": "Reasoning, Summarization, Coding",
        "recommended": True,
        "url": "https://huggingface.co/bartowski/Phi-3.5-mini-instruct-GGUF/resolve/main/Phi-3.5-mini-instruct-Q4_K_M.gguf"
    },
    {
        "id": "Mistral-7B-Instruct-v0.3.Q4_K_M",
        "name": "Mistral 7B Instruct v0.3",
        "description": "Updated Mistral 7B with larger vocabulary and better performance.",
        "size": "4.37 GB",
        "size_bytes": 4690000000,
        "ram_required": 8,
        "category": "large",
        "quantization": "Q4_K_M",
        "use_case": "General, Summarization, Reliable Instructions",
        "recommended": True,
        "url": "https://huggingface.co/maziyarpanahi/Mistral-7B-Instruct-v0.3-GGUF/resolve/main/Mistral-7B-Instruct-v0.3.Q4_K_M.gguf"
    },
    {
        "id": "gemma-2-2b-it.Q4_K_M",
        "name": "Gemma 2 2B Instruct",
        "description": "Google's best-in-class small model (2.6B). High quality in a small package.",
        "size": "1.7 GB",
        "size_bytes": 1800000000,
        "ram_required": 5,
        "category": "medium",
        "quantization": "Q4_K_M",
        "use_case": "Chat, Summarization, Fast Responses",
        "recommended": True,
        "url": "https://huggingface.co/bartowski/gemma-2-2b-it-GGUF/resolve/main/gemma-2-2b-it-Q4_K_M.gguf"
    },
    {
        "id": "openchat-3.5-0106.Q4_K_M",
        "name": "OpenChat 3.5 (0106)",
        "description": "Consistently high-ranking open source model for reasoning and chat.",
        "size": "4.37 GB",
        "size_bytes": 4690000000,
        "ram_required": 8,
        "category": "large",
        "quantization": "Q4_K_M",
        "use_case": "Chat, Complex Instructions, Summarization",
        "recommended": False,
        "url": "https://huggingface.co/TheBloke/openchat-3.5-0106-GGUF/resolve/main/openchat-3.5-0106.Q4_K_M.gguf"
    },
    
    # ============================================================
    # HIGH-QUALITY QUANTIZATIONS (Q5, Q6, Q8) - For users with more RAM
    # ============================================================
    {
        "id": "Meta-Llama-3-8B-Instruct.Q5_K_M",
        "name": "Llama 3 8B Instruct (Q5 - Higher Quality)",
        "description": "Higher quality quantization. Better accuracy than Q4, slightly larger.",
        "size": "5.73 GB",
        "size_bytes": 6150000000,
        "ram_required": 12,
        "category": "large",
        "quantization": "Q5_K_M",
        "use_case": "Premium Summarization, Reasoning",
        "recommended": False,
        "url": "https://huggingface.co/MaziyarPanahi/Meta-Llama-3-8B-Instruct-GGUF/resolve/main/Meta-Llama-3-8B-Instruct.Q5_K_M.gguf"
    },
    {
        "id": "Meta-Llama-3-8B-Instruct.Q6_K",
        "name": "Llama 3 8B Instruct (Q6 - Near Original)",
        "description": "Near-original quality. Minimal quality loss from full precision.",
        "size": "6.60 GB",
        "size_bytes": 7080000000,
        "ram_required": 14,
        "category": "large",
        "quantization": "Q6_K",
        "use_case": "Maximum Quality 8B Inference",
        "recommended": False,
        "url": "https://huggingface.co/MaziyarPanahi/Meta-Llama-3-8B-Instruct-GGUF/resolve/main/Meta-Llama-3-8B-Instruct.Q6_K.gguf"
    },
    {
        "id": "Meta-Llama-3-8B-Instruct.Q8_0",
        "name": "Llama 3 8B Instruct (Q8 - Best Quality)",
        "description": "Highest quality 8-bit quantization. Virtually identical to original.",
        "size": "8.54 GB",
        "size_bytes": 9170000000,
        "ram_required": 16,
        "category": "premium",
        "quantization": "Q8_0",
        "use_case": "Best Possible 8B Quality",
        "recommended": True,
        "url": "https://huggingface.co/MaziyarPanahi/Meta-Llama-3-8B-Instruct-GGUF/resolve/main/Meta-Llama-3-8B-Instruct.Q8_0.gguf"
    },
    {
        "id": "Mistral-7B-Instruct-v0.3.Q8_0",
        "name": "Mistral 7B Instruct v0.3 (Q8 - Best Quality)",
        "description": "Maximum quality Mistral. Excellent for document summarization.",
        "size": "7.70 GB",
        "size_bytes": 8270000000,
        "ram_required": 14,
        "category": "premium",
        "quantization": "Q8_0",
        "use_case": "Premium Summarization, Analysis",
        "recommended": False,
        "url": "https://huggingface.co/MaziyarPanahi/Mistral-7B-Instruct-v0.3-GGUF/resolve/main/Mistral-7B-Instruct-v0.3.Q8_0.gguf"
    },
    
    # ============================================================
    # EXTRA-LARGE MODELS (13B) - Requires 16GB+ RAM
    # ============================================================
    {
        "id": "llama-2-13b-chat.Q4_K_M",
        "name": "Llama 2 13B Chat",
        "description": "Meta's 13B parameter model. Significantly smarter than 7B variants.",
        "size": "7.87 GB",
        "size_bytes": 8450000000,
        "ram_required": 16,
        "category": "extra-large",
        "quantization": "Q4_K_M",
        "use_case": "Advanced Chat, Complex Reasoning",
        "recommended": True,
        "url": "https://huggingface.co/TheBloke/Llama-2-13B-chat-GGUF/resolve/main/llama-2-13b-chat.Q4_K_M.gguf"
    },
    {
        "id": "llama-2-13b-chat.Q5_K_M",
        "name": "Llama 2 13B Chat (Q5 - Higher Quality)",
        "description": "Higher quality 13B. Best balance for 32GB RAM systems.",
        "size": "9.23 GB",
        "size_bytes": 9910000000,
        "ram_required": 18,
        "category": "extra-large",
        "quantization": "Q5_K_M",
        "use_case": "Premium Chat, Deep Analysis",
        "recommended": True,
        "url": "https://huggingface.co/TheBloke/Llama-2-13B-chat-GGUF/resolve/main/llama-2-13b-chat.Q5_K_M.gguf"
    },
    {
        "id": "codellama-13b-instruct.Q4_K_M",
        "name": "Code Llama 13B Instruct",
        "description": "Meta's code-focused 13B model. Excellent for code analysis.",
        "size": "7.87 GB",
        "size_bytes": 8450000000,
        "ram_required": 16,
        "category": "extra-large",
        "quantization": "Q4_K_M",
        "use_case": "Code Analysis, Programming",
        "recommended": False,
        "url": "https://huggingface.co/TheBloke/CodeLlama-13B-Instruct-GGUF/resolve/main/codellama-13b-instruct.Q4_K_M.gguf"
    },
    {
        "id": "mixtral-8x7b-instruct-v0.1.Q4_K_M",
        "name": "Mixtral 8x7B Instruct (MoE)",
        "description": "Mistral's MoE model. 46.7B params, only uses ~13B actively. Very capable.",
        "size": "26.4 GB",
        "size_bytes": 28350000000,
        "ram_required": 28,
        "category": "extra-large",
        "quantization": "Q4_K_M",
        "use_case": "Expert-level Tasks, Complex Analysis",
        "recommended": True,
        "url": "https://huggingface.co/TheBloke/Mixtral-8x7B-Instruct-v0.1-GGUF/resolve/main/mixtral-8x7b-instruct-v0.1.Q4_K_M.gguf"
    },
    {
        "id": "nous-hermes-2-mixtral-8x7b-dpo.Q4_K_M",
        "name": "Nous Hermes 2 Mixtral 8x7B",
        "description": "Fine-tuned Mixtral with improved instruction following.",
        "size": "26.4 GB",
        "size_bytes": 28350000000,
        "ram_required": 28,
        "category": "extra-large",
        "quantization": "Q4_K_M",
        "use_case": "Advanced Instructions, Research",
        "recommended": False,
        "url": "https://huggingface.co/TheBloke/Nous-Hermes-2-Mixtral-8x7B-DPO-GGUF/resolve/main/nous-hermes-2-mixtral-8x7b-dpo.Q4_K_M.gguf"
    },
    {
        "id": "deepseek-coder-6.7b-instruct.Q5_K_M",
        "name": "DeepSeek Coder 6.7B (Q5)",
        "description": "Excellent for code understanding and analysis in documents.",
        "size": "5.00 GB",
        "size_bytes": 5370000000,
        "ram_required": 10,
        "category": "large",
        "quantization": "Q5_K_M",
        "use_case": "Code Review, Technical Docs",
        "recommended": False,
        "url": "https://huggingface.co/TheBloke/deepseek-coder-6.7B-instruct-GGUF/resolve/main/deepseek-coder-6.7b-instruct.Q5_K_M.gguf"
    },
    {
        "id": "yi-1.5-9b-chat.Q5_K_M",
        "name": "Yi 1.5 9B Chat (Q5)",
        "description": "01.AI's powerful 9B model. Strong multilingual and reasoning.",
        "size": "6.50 GB",
        "size_bytes": 6980000000,
        "ram_required": 12,
        "category": "large",
        "quantization": "Q5_K_M",
        "use_case": "Multilingual, Advanced Reasoning",
        "recommended": False,
        "url": "https://huggingface.co/mradermacher/Yi-1.5-9B-Chat-GGUF/resolve/main/Yi-1.5-9B-Chat.Q5_K_M.gguf"
    },
    {
        "id": "solar-10.7b-instruct-v1.0.Q4_K_M",
        "name": "Solar 10.7B Instruct",
        "description": "Upstage's 10.7B model. Top performer in its class.",
        "size": "6.46 GB",
        "size_bytes": 6940000000,
        "ram_required": 12,
        "category": "large",
        "quantization": "Q4_K_M",
        "use_case": "Instructions, Analysis, Chat",
        "recommended": False,
        "url": "https://huggingface.co/TheBloke/SOLAR-10.7B-Instruct-v1.0-GGUF/resolve/main/solar-10.7b-instruct-v1.0.Q4_K_M.gguf"
    },
    {
        "id": "qwen2-7b-instruct.Q5_K_M",
        "name": "Qwen 2 7B Instruct (Q5)",
        "description": "Alibaba's latest. Excellent multilingual and coding capabilities.",
        "size": "5.50 GB",
        "size_bytes": 5900000000,
        "ram_required": 10,
        "category": "large",
        "quantization": "Q5_K_M",
        "use_case": "Multilingual, Code, General",
        "recommended": True,
        "url": "https://huggingface.co/Qwen/Qwen2-7B-Instruct-GGUF/resolve/main/qwen2-7b-instruct-q5_k_m.gguf"
    }
]

download_status = {
    "downloading": False,
    "model_id": None,
    "progress": 0,
    "error": None,
    "bytes_downloaded": 0,
    "total_bytes": 0
}

def get_available_models():
    return AVAILABLE_MODELS

def get_local_models():
    """Return list of downloaded models with path, name, and size."""
    models = []
    if os.path.exists(MODELS_DIR):
        for f in os.listdir(MODELS_DIR):
            if f.endswith(".gguf"):
                filepath = os.path.join(MODELS_DIR, f)
                size = os.path.getsize(filepath)
                
                # Try to find metadata from AVAILABLE_MODELS
                model_id = f.replace(".gguf", "")
                available_model = next((m for m in AVAILABLE_MODELS if m["id"] == model_id), None)
                
                models.append({
                    "id": model_id,
                    "filename": f,
                    "path": os.path.abspath(filepath),
                    "size": size,
                    "name": available_model["name"] if available_model else f.replace(".gguf", "").replace("-", " ").replace(".", " "),
                    "category": available_model["category"] if available_model else "unknown",
                    "ram_required": available_model["ram_required"] if available_model else None
                })
    return models

def check_system_resources(model):
    """Check if system has enough resources for the model."""
    warnings = []
    can_download = True
    
    # Check available disk space
    disk_usage = shutil.disk_usage(MODELS_DIR)
    available_gb = disk_usage.free / (1024**3)
    required_gb = model.get("size_bytes", 0) / (1024**3) * 1.1  # 10% buffer
    
    if available_gb < required_gb:
        warnings.append(f"Low disk space: {available_gb:.1f}GB available, {required_gb:.1f}GB needed")
        can_download = False
    
    # Check available RAM
    ram_info = psutil.virtual_memory()
    available_ram_gb = ram_info.available / (1024**3)
    required_ram_gb = model.get("ram_required", 4)
    
    if available_ram_gb < required_ram_gb:
        warnings.append(f"Low RAM: {available_ram_gb:.1f}GB available, {required_ram_gb}GB recommended")
        # Don't block download for RAM, just warn
    
    return can_download, warnings

def download_file(url, filename, model_id, total_bytes=0):
    global download_status
    filepath = os.path.join(MODELS_DIR, filename)
    temp_filepath = filepath + ".partial"
    
    try:
        print(f"Starting download: {url}")
        download_status = {
            "downloading": True, 
            "model_id": model_id, 
            "progress": 0, 
            "error": None,
            "bytes_downloaded": 0,
            "total_bytes": total_bytes
        }
        
        # Check for partial download (resume support)
        headers = {}
        downloaded = 0
        if os.path.exists(temp_filepath):
            downloaded = os.path.getsize(temp_filepath)
            headers["Range"] = f"bytes={downloaded}-"
            print(f"Resuming from byte {downloaded}")
        
        response = requests.get(url, stream=True, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Get total size from headers
        if "content-range" in response.headers:
            total_size = int(response.headers.get("content-range", "").split("/")[-1])
        else:
            total_size = int(response.headers.get('content-length', 0)) + downloaded
        
        download_status["total_bytes"] = total_size
        block_size = 1024 * 1024  # 1MB
        
        mode = 'ab' if downloaded > 0 else 'wb'
        with open(temp_filepath, mode) as file:
            for data in response.iter_content(block_size):
                downloaded += len(data)
                file.write(data)
                if total_size > 0:
                    download_status["progress"] = int((downloaded / total_size) * 100)
                    download_status["bytes_downloaded"] = downloaded
        
        # Rename to final filename
        os.rename(temp_filepath, filepath)
        
        print(f"Download complete: {filename}")
        download_status = {
            "downloading": False, 
            "model_id": None, 
            "progress": 100, 
            "error": None,
            "bytes_downloaded": downloaded,
            "total_bytes": total_size
        }
        
    except Exception as e:
        print(f"Download failed: {e}")
        download_status = {
            "downloading": False, 
            "model_id": model_id, 
            "progress": 0, 
            "error": str(e),
            "bytes_downloaded": 0,
            "total_bytes": 0
        }
        # Keep partial file for resume

def start_download(model_id):
    global download_status
    
    if download_status["downloading"]:
        return False, "Another download is in progress"
    
    model = next((m for m in AVAILABLE_MODELS if m["id"] == model_id), None)
    if not model:
        return False, f"Model not found: {model_id}"
    
    filename = f"{model_id}.gguf"
    filepath = os.path.join(MODELS_DIR, filename)
    
    # Check if already downloaded
    if os.path.exists(filepath):
        return False, "Model already downloaded"
    
    # Check system resources
    can_download, warnings = check_system_resources(model)
    if not can_download:
        return False, f"Cannot download: {'; '.join(warnings)}"
    
    thread = threading.Thread(
        target=download_file, 
        args=(model["url"], filename, model_id, model.get("size_bytes", 0))
    )
    thread.daemon = True
    thread.start()
    
    warning_msg = f" (Warnings: {'; '.join(warnings)})" if warnings else ""
    return True, f"Download started{warning_msg}"

def get_download_status():
    return download_status

def is_safe_model_path(path):
    """
    Validate that the path is strictly within the MODELS_DIR.
    Prevents path traversal and arbitrary file operations.
    """
    if not path:
        return False

    try:
        # Resolve absolute paths
        abs_path = os.path.abspath(path)
        abs_models_dir = os.path.abspath(MODELS_DIR)

        # Check if path is within MODELS_DIR
        # os.path.commonpath returns the longest common sub-path
        # We ensure the common path IS the models directory
        common = os.path.commonpath([abs_path, abs_models_dir])

        # 1. Must be inside models dir
        # 2. Must not BE the models dir itself (prevent deleting the folder)
        return common == abs_models_dir and abs_path != abs_models_dir

    except Exception:
        return False

def delete_model(model_path):
    """Delete a downloaded model file."""
    if not is_safe_model_path(model_path):
        print(f"Security Warning: Attempt to delete unsafe path: {model_path}")
        return False

    if os.path.exists(model_path):
        try:
            os.remove(model_path)
            return True
        except OSError as e:
            print(f"Error deleting model: {e}")
            return False
    return False
