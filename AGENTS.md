# File Search Engine - Workspace Instructions

> AI-powered local document search with semantic search, LLM integration, and modern React frontend.
> **Always read and update the Change Log section after making any changes.**

## Quick Start
```bash
npm run install-all    # Install all dependencies
npm run start          # Start backend (8000) + frontend (5173)
```

## Tech Stack

**Backend (Python 3.8+):**
- FastAPI - REST API with async support
- FAISS - Vector similarity search
- LangChain - LLM integration framework
- LlamaCpp - Local GGUF model inference
- SQLite - Metadata storage (`metadata.db`)

**Frontend (Node.js 16+):**
- React 19 + Vite - UI framework with HMR
- TailwindCSS - Utility-first styling
- Framer Motion - Animations
- Vitest - Testing (not Jest!)
- Axios - HTTP client

## Project Structure
```
├── backend/                # Python backend code
│   ├── __init__.py         # Package marker
│   ├── api.py              # FastAPI endpoints (main entry)
│   ├── database.py         # SQLite CRUD operations
│   ├── indexing.py         # FAISS index creation
│   ├── search.py           # Semantic search logic
│   ├── file_processing.py  # Text extraction (PDF, DOCX, XLSX, PPTX, TXT)
│   ├── llm_integration.py  # LLM provider abstraction
│   ├── model_manager.py    # GGUF model downloads
│   ├── background.py       # Background task utilities
│   └── tests/              # pytest tests
│       ├── test_api.py, test_database.py, test_search.py
│       ├── test_indexing.py, test_file_processing.py
│       └── test_llm_integration_full.py
├── frontend/               # React frontend
│   ├── src/
│   │   ├── App.jsx         # Main component (holds global state)
│   │   ├── components/     # UI components
│   │   │   ├── Header.jsx, SearchBar.jsx, SearchResults.jsx
│   │   │   ├── SettingsModal.jsx, ModelManager.jsx
│   │   │   └── SearchHistory.jsx, FileList.jsx, BenchmarkResults.jsx
│   │   └── test/           # Vitest tests
│   └── package.json
├── scripts/                # Utility scripts
│   ├── start_all.js        # Unified startup script
│   ├── run_tests.py        # Test runner
│   └── benchmark_models.py # Model benchmarking
├── data/                   # Generated/runtime files
│   ├── index.faiss         # Vector embeddings
│   ├── index_docs.pkl      # Document chunks
│   ├── index_tags.pkl      # Tag data
│   ├── metadata.db         # SQLite database
│   └── benchmark_results.json
├── models/                 # Downloaded GGUF models
├── .agent/                 # Agent configuration and skills
├── config.ini              # User configuration
├── requirements.txt        # Python dependencies
└── package.json            # Node.js scripts
```

### File Placement Protocol
- **Backend Code**: ALL Python source files MUST go in `backend/` or `backend/tests/`.
  - Exception: `api.py` is the entry point (in `backend/`).
  - NO `.py` files in the project root.
- **Scripts**: Maintenance, build, and benchmark scripts go in `scripts/`.
- **Data**: All generated files (`.db`, `.faiss`, `.log`, `.json` results) MUST go in `data/`.
  - Use `DATA_DIR` constant in code.
- **Models**: Large model binaries go in `models/` (root) but code must reference `MODELS_DIR`.
- **Tests**: 
  - Backend tests: `backend/tests/`
  - Frontend tests: `frontend/src/test/`
- **Validation**: Run `npm run validate` to check structure compliance.

## Code Patterns

### LLM Provider Pattern (`llm_integration.py`)
```python
# Get embeddings - works with any provider
embeddings = get_embeddings(provider='openai', api_key='sk-...')
embeddings = get_embeddings(provider='local')  # Uses HuggingFace

# Get LLM client for generation
client = get_llm_client(provider='gemini', api_key='...')
response = client.invoke("Your prompt")

# Caches: _embeddings_cache, _llm_cache (avoid reloading)
```

### Database Pattern (`database.py`)
```python
def db_operation(params):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SQL", (params,))
    result = cursor.fetchone()  # or fetchall()
    conn.commit()  # For INSERT/UPDATE/DELETE
    conn.close()
    return result
```

### API Pattern (`api.py`)
```python
@app.post("/api/endpoint")
def endpoint(request: RequestModel, background_tasks: BackgroundTasks):
    # For long operations, use background_tasks.add_task(func, args)
    return {"status": "success", "data": result}
```

### Frontend Component Pattern
```jsx
export default function Component({ prop, onAction }) {
    const [state, setState] = useState(null)
    const [loading, setLoading] = useState(false)
    
    useEffect(() => {
        fetchData()
    }, [])
    
    return <div className="bg-gray-900 p-4 rounded-lg">...</div>
}
```

### Frontend API Pattern
```jsx
const API = 'http://localhost:8000'
try {
    const response = await axios.post(`${API}/api/search`, { query })
    setResults(response.data.results)
} catch (error) {
    console.error('Error:', error)
}
```

## Testing

### Commands
```bash
# Backend
npm run test              # Quick (~12s)
npm run test:full         # With models (~10min)
python run_tests.py --coverage

# Frontend
cd frontend && npm run test
```

### Backend Test Pattern
```python
class TestFeature(unittest.TestCase):
    def test_behavior(self):
        result = function()
        self.assertEqual(result, expected)
    
    # ALWAYS mock LLM calls to avoid API costs
    @patch('llm_integration.get_llm_client')
    def test_with_llm(self, mock_client):
        mock_client.return_value.invoke.return_value = MagicMock(content="AI text")
        result = function_using_llm()
        self.assertIn("AI", result)
```

### Frontend Test Pattern
```jsx
import { describe, it, expect, vi } from 'vitest'

describe('Component', () => {
    it('should work', () => {
        const mockFn = vi.fn()
        mockFn('arg')
        expect(mockFn).toHaveBeenCalledWith('arg')
    })
})
```

## API Reference

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/config` | Get configuration |
| POST | `/api/config` | Update configuration |
| POST | `/api/search` | Semantic search with AI summaries |
| GET | `/api/search/history` | Get search history |
| DELETE | `/api/search/history/{id}` | Delete history item |
| DELETE | `/api/search/history` | Clear all history |
| POST | `/api/index` | Start background indexing |
| GET | `/api/index/status` | Get indexing progress |
| GET | `/api/files` | List indexed files |
| GET | `/api/folders/history` | Get folder history |
| DELETE | `/api/folders/history` | Clear all folder history |
| DELETE | `/api/folders/history/item` | Delete single folder from history |
| POST | `/api/validate-path` | Validate folder path |
| POST | `/api/open-file` | Open file in system app |
| GET | `/api/models/available` | Downloadable models |
| GET | `/api/models/local` | Downloaded models |
| POST | `/api/models/download/{id}` | Start download |
| GET | `/api/models/status` | Download progress |
| DELETE | `/api/models` | Delete model |
| POST | `/api/benchmarks/run` | Run benchmarks |
| GET | `/api/benchmarks/results` | Get results |
| GET | `/api/cache/stats` | Get AI response cache stats |
| POST | `/api/cache/clear` | Clear AI response cache |

## Common Tasks

### Add API Endpoint
1. Add Pydantic model + route in `api.py`
2. Add test in `tests/test_api.py` with mocks
3. Call from frontend using axios

### Add LLM Provider
1. Add to `get_llm_client()` in `llm_integration.py`
2. Add to `get_embeddings()` in `llm_integration.py`
3. Add API key handling in `api.py` config endpoints
4. Update `SettingsModal.jsx` provider dropdown

### Add File Type
1. Add case in `file_processing.py:extract_text()`
2. Add mock test in `tests/test_file_processing.py`

### Add React Component
1. Create `frontend/src/components/Name.jsx`
2. Create `frontend/src/test/Name.test.jsx`
3. Import in parent component

## Configuration
```ini
[General]
folders = C:/path/folder1,C:/path/folder2
auto_index = false

[APIKeys]
openai_api_key = sk-...
gemini_api_key = ...
anthropic_api_key = ...

[LocalLLM]
provider = local
model_path = models/phi-2.Q4_K_M.gguf
```

**Providers:** `local` (free, needs RAM), `openai`, `gemini`, `anthropic`, `grok`

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Index not loaded" | Settings → Add folder → Rebuild Index |
| Model download fails | Check disk space, try TinyLlama (637MB) |
| Out of memory | Use smaller model or cloud provider |
| No search results | Broader terms, re-index folder |
| CORS errors | Backend :8000, Frontend :5173 |

## Agent Skills

When working on file processing tasks, consult the relevant skill documentation:

| File Type | Skill Location |
|-----------|----------------|
| PDF (.pdf) | `.agent/skills/pdf/SKILL.md` |
| Word (.docx) | `.agent/skills/docx/SKILL.md` |
| Excel (.xlsx, .xls) | `.agent/skills/xlsx/SKILL.md` |
| PowerPoint (.pptx) | `.agent/skills/pptx/SKILL.md` |

**Usage**: Before modifying `file_processing.py` or adding new file type support, read the corresponding skill file for best practices and patterns.

---

## Mandatory Rules

1. **Run tests before AND after changes** - `npm run test`
2. **Mock all LLM calls** in tests to avoid costs
3. **Frontend uses Vitest** - import from 'vitest', not jest
4. **Check existing patterns** before implementing
5. **Update Change Log** after every modification

## Golden Dataset (Testing)

A standardized "Golden Dataset" is available for verifying retrieval accuracy across different file types.

**Location**: `data/golden_dataset/`

**Scripts**:
*   `python scripts/create_golden_dataset.py`: Generates synthetic files (PDF, DOCX, XLSX, PPTX) and downloads real-world samples.
*   `python scripts/verify_golden_set.py`: Indexes the dataset and runs "needle-in-a-haystack" queries to verify accuracy.

**Usage**:
Run this before major releases to ensure core functionality works:
```bash
python scripts/create_golden_dataset.py
python scripts/verify_golden_set.py
```

---

## Change Log

> **CRITICAL: Add entry here after EVERY change with date, description, and files.**

### 2026-01-30 (Security)
- **Fixed Arbitrary File Deletion Vulnerability**
  - **fix**: Implemented `is_safe_model_path` validation in `model_manager.py` to prevent path traversal in model deletion.
  - **test**: Added `backend/tests/test_security.py` with regression tests.
  - **Files**: `backend/model_manager.py`, `backend/tests/test_security.py`, `scripts/run_tests.py`

### 2026-01-30
- **Optimized Startup Health Checks & Backend Performance**
  - **feat**: Modified `scripts/start_all.js` with increased health check intervals (3s), longer timeouts (120s), and "localhost" binding for better Windows reliability.
  - **feat**: Suppressed noisy health check error logs during initial startup phase.
  - **perf**: Implemented non-blocking backend startup by moving heavy `load_index()` into an asynchronous background thread (`asyncio.to_thread`).
  - **perf**: Implemented lazy loading for heavy backend modules (`langchain`, `llama-cpp`, `tkinter`) to reduce initial Python process cold-start time.
  - **feat**: Added dedicated lightweight `/api/health` endpoint for reliable service readiness verification.
  - **Files**: `scripts/start_all.js`, `backend/api.py`

### 2026-01-30 (Part 2)
- **Expanded Frontend Test Coverage**
  - **feat**: Implemented comprehensive functional UI tests for `SearchHistory` and `FileList` components.
  - **fix**: Upgraded `SettingsModal`, `ModelManager`, `SearchBar`, and `SearchResults` tests to use `@testing-library/react` interactions instead of basic logic checks.
  - **verification**: Validated all "Delete", "Clear All", and "Open File" workflows with 100% pass rate (47 tests).
  - **accessibility**: Added `title` attributes to `SearchResults` and `ModelManager` buttons for better testability and accessibility.
  - **Files**: `frontend/src/test/*.test.jsx`, `frontend/src/components/SearchResults.jsx`

### 2026-01-30
- **Fixed Duplicate Search Results & Context Window Overflow**
  - **fix**: Improved search deduplication to strict "one result per file" + content hashing to eliminate near-duplicates
  - **fix**: Reduced context truncation from 10000 to 3000 chars to prevent exceeding 4096 token context window on local LLMs
  - **fix**: Limited AI context snippets from 4 to 2, each capped at 400 chars
  - **Files**: `backend/search.py`, `backend/llm_integration.py`, `backend/api.py`
- **Fixed File Path Not Showing in Search Results**
  - **fix**: Search results now use file_path from FAISS metadata first (instead of failing database lookup)
  - **Files**: `backend/api.py`
- **Auto-Cleanup Test Data After Tests**
  - **feat**: Added `cleanup_test_data()` to `database.py` to remove temp/test paths from production database
  - **feat**: Test runner now automatically cleans up test data after successful test runs
- [x] Verification: Test strict query "Where did Siddhesh work" <!-- id: 2 -->
    - [x] Verified resume retrieved as top 3 results
    - [x] Verified AI answer synthesize information from multiple files
- **Expanded AI Context to Multi-File Synthesis**
  - **feat**: Increased AI context to include top 6 results (up from 2)
  - **feat**: Increased context truncation limit from 3000 to 10000 chars in `llm_integration.py`
  - **Files**: `backend/api.py`, `backend/llm_integration.py`

### 2026-01-27 (Maintenance)
- **Fixed Dependency & Added Logging** - Resolved explicit dependency error and added full-stack logging
  - **Backend**: Added `sentence-transformers==3.0.1` to `requirements.txt`
  - **Backend**: Implemented centralized logging to `data/app.log` in `api.py`
  - **Frontend**: Added `logger.js` utility and global error handling in `main.jsx`
  - **Files**: `requirements.txt`, `backend/api.py`, `frontend/src/lib/logger.js`, `frontend/src/main.jsx`
- **Implemented Indexing Progress Bar** - Added granular progress tracking for RAPTOR indexing
  - **Backend**: Updated `indexing.py` to report weighted progress for extraction, embedding, and summarization
  - **Frontend**: Updated `SettingsModal.jsx` to show detailed status messages
  - **Files**: `backend/indexing.py`, `backend/api.py`, `frontend/src/components/SettingsModal.jsx`
- **Fixed Sentence Transformers Import** - Resolved dependency error for local embeddings
  - **Dependencies**: Added `langchain-huggingface==0.0.3` to requirements
  - **Verification**: Created `scripts/verify_imports.py` to confirm successful loading
  - **Files**: `requirements.txt`, `backend/llm_integration.py`
- **Fixed Dependency Conflicts** - Resolved `langchain-core` vs `langchain-huggingface` incompatibility
  - **Dependencies**: Upgraded `langchain` stack and `langchain-huggingface==1.2.0` in `venv_new`
  - **Verification**: Verified successful installation of compatible versions
  - **Files**: `requirements.txt`
- **Fixed Local Model "No Response"** - Resolved missing `llama_cpp` import
  - **Fix**: Added `from llama_cpp import Llama` in `backend/llm_integration.py`
  - **Enhancement**: Added full logging to `backend/api.py` search endpoint
  - **Files**: `backend/llm_integration.py`, `backend/api.py`
- **Fixed Llama.cpp Crash** - Added thread locking for local model inference
  - **Issue**: `GGML_ASSERT` crash due to concurrent access to single `Llama` instance
  - **Fix**: Implemented `threading.Lock()` in `backend/llm_integration.py`
  - **Files**: `backend/llm_integration.py`
- **Optimized Local Indexing** - Disabled slow LLM summarization for clusters on local provider
  - **Fix**: Switched to fast regex-based summary in `backend/indexing.py` for `local` provider
  - **Result**: Indexing time reduced from ~20mins to seconds
  - **Files**: `backend/indexing.py`
- **Fixed Startup Timeout** - Optimized backend loading sequence
  - **Issue**: `Llama` import blocking main thread for >20s, causing frontend runner timeout
  - Files: `backend/llm_integration.py`, `scripts/start_all.js`
- **Performance Optimization** - significantly improved local model response time
  - **Enhancement**: Increased local LLM thread count from 4 to dynamic (~16 on user's 20-thread CPU)
  - **Enhancement**: Enabled GPU offloading (`n_gpu_layers=-1`) for supported hardware
  - **Optimization**: Reduced "Smart Summary" calls in Search API from top 3 to top 1 document (saving ~10s per query)
  - **Files**: `backend/llm_integration.py`, `backend/api.py`
- **Identity Accuracy & Multi-GPU Support** - fixed "Siddharth vs Siddhesh" confusion
  - **Fix**: Implemented "Identity/Exact Match Boost" in `search.py` to favor exact name matches in queries.
  - **Fix**: Updated LLM system prompt to strictly distinguish between similar names and identities.
  - **Enhancement**: Added `tensor_split` support in `config.ini` for splitting models across multiple GPUs (e.g., `[0.5, 0.5]`).
  - **Files**: `backend/search.py`, `backend/llm_integration.py`, `backend/api.py`
- **Agentic Reasoning Fixes** - Fixed tool execution and parsing errors
  - **Fix**: Resolved `AttributeError` and `TypeError` in `search_knowledge_base` and `list_files` tools.
  - **Enhancement**: Improved `read_file` tool to automatically resolve filenames to full system paths via database lookup.
  - **Fix**: Updated ReAct agent system prompt and regex parsing for more robust tool usage and formatting.
  - **Files**: `backend/agent.py`, `backend/tools.py`, `backend/database.py`
- **Startup Stability & Health Checks** - Resolved health check timeouts
  - **Fix**: Added `@app.get("/")` and `@app.get("/api/health")` to `api.py` for reliable startup verification.
  - **Optimization**: Offloaded local model warmup to a background thread using `asyncio.to_thread` with a delay.
  - **Fix**: Prevented main event loop blockage during large model loading.
  - **Files**: `backend/api.py`
- **Port Reliability & System Visibility** - Added auto-cleanup and verbose logs
  - **feat**: Modified `scripts/start_all.js` to automatically terminate zombie processes on ports 8000 and 5173 before startup.
  - **feat**: Integrated verbose print statements across `api.py`, `agent.py`, `search.py`, and `llm_integration.py`.
  - **Info**: AI Researcher mode now logs every thought, action, and tool observation to the backend console for real-time debugging.
  - **Files**: `scripts/start_all.js`, `backend/agent.py`, `backend/search.py`, `backend/llm_integration.py`, `backend/api.py`
- **Agent Self-Correction & Robustness** - Improved reliability on local LLMs
  - **feat**: Implemented an "Error-Feedback" loop in `agent.py`. If the agent fails to format an action correctly, the error is fed back to its history as an `Observation`, allowing it to self-correct.
  - **feat**: Added fallback regex parsing for `tool_name("input")` syntax, handling cases where LLMs deviate from ReAct formatting.
  - **fix**: Added proactive "nudges" in the history if the agent provides a thought without an accompanying action.
  - **Files**: `backend/agent.py`
- **Blazing Fast Inference Optimizations** - Maximized local LLM throughput
  - **perf**: Enabled **Flash Attention**, **f16_kv**, and **offload_kqv** in `llm_integration.py` for significant speedups.
  - **perf**: Optimized thread allocation for both prompt processing (`n_threads`) and batch generation (`n_threads_batch`).
  - **perf**: Implemented context truncation (10k chars) to prevent prompt-processing stalls on huge document sets.
  - **perf**: Switched to greedy decoding (temp 0.1-0.2) in Agent and Answer modes for faster token generation.
  - **Files**: `backend/llm_integration.py`, `backend/agent.py`
- **Quality & Data Structure Optimizations** - High speed without compromise
  - **feat**: Implemented **Parallel Hybrid Search**. Semantic (FAISS) and Keyword (BM25) searches now run concurrently using `ThreadPoolExecutor`.
  - **perf**: Added **SQLite B-Tree Indices** to `files` table (`faiss_start_idx`, `faiss_end_idx`, `filename`) for $O(\log N)$ metadata lookups.
  - **feat**: Upgraded `search.py` tokenizer with a custom **Stop-Word Filter** to improve keyword precision and result quality.
  - **Info**: Maintained **FAISS FlatL2** index type to ensure 100% exact retrieval accuracy (No approximation compromise).
  - **Files**: `backend/search.py`, `backend/database.py`
- **UX & Search Quality Improvements**
  - **fix**: Implemented **Search Result Diversification**. The search engine now enforces a "Max 2 Chunks Per File" rule (soft limit) to prevent a single large document from dominating all search results.
  - **test**: Created `tests/test_api.py` to verify the `/api/open-file` endpoint functionality and error handling.
  - **clean**: Renamed temporary `test_api_extra.py` to standard `tests/test_api.py` to adhere to project structure rules.
  - **Files**: `backend/search.py`, `tests/test_api.py`

- **Advanced Model Stress Testing & Ranking**
  - **feat**: Created `backend/tests/test_model_stress.py` for rigorous performance evaluation.
  - **feat**: Implemented weighted scoring system (TPS, Accuracy, Load Time, Memory) in `scripts/benchmark_models.py`.
  - **test**: Successfully ranked 5 local models; identified TinyLlama and Gemma as top performers.
  - **Files**: `backend/tests/test_model_stress.py`, `scripts/benchmark_models.py`, `AGENTS.md`
  - **Verification**: Ran full stress suite (9-minute run); all tests passed with valid performance data.

- **Refined Folder History**

  - "Recent History" now STRICTLY filters for "100% indexed" folders.
  - Added `is_indexed` column to `folder_history` table.
  - Files: `backend/database.py`, `backend/api.py`
- **Fixed Search Critical Bugs**
  - Resolved `NameError` and `UnboundLocalError` in Search API.
  - Fixed `database` import scope issues in `api.py` and `llm_integration.py`.
  - Files: `backend/api.py`, `backend/llm_integration.py`
- **Fixed Startup Timeout**
  - Restored `log` function and `colors` object in `scripts/start_all.js` to fix `ReferenceError`.
  - Increased health check timeout to 90s and forced `127.0.0.1` binding.
  - Files: `scripts/start_all.js`
- **Fixed Frontend Port Mismatch**
  - Configured `vite.config.js` to strictly use `host: 127.0.0.1` and `port: 5173`.
  - Files: `frontend/vite.config.js`

### 2026-01-21 (UI Redesign)
- **Implemented Cosmic Glassmorphism UI** - Complete visual overhaul
  - `frontend/src/index.css`: New cosmic color palette, glass utilities, animations
  - `frontend/tailwind.config.js`: Cosmic colors, glow keyframes
  - `frontend/src/components/CosmicBackground.jsx`: **NEW** - Particle effects component
  - `frontend/src/App.jsx`: Cosmic background integration
  - `frontend/src/components/Header.jsx`: Glass nav, gradient logo, model dropdown
  - `frontend/src/components/SearchBar.jsx`: Glass input, animated focus, agent toggle
  - `frontend/src/components/SearchResults.jsx`: Glass cards, AI sidebar, file icons
  - `frontend/src/components/SettingsModal.jsx`: Glass overlay, cosmic buttons

### 2026-01-21 (Startup Fixes)
- **Fixed virtual environment issues** - Created `venv_new` to bypass file lock issues
  - Updated `package.json` and `scripts/start_all.js` to use `venv_new`
  - Added `venv_new/` to `.gitignore`
- **Pinned missing dependencies** - Added `scikit-learn==1.8.0` and `rank-bm25==0.2.2` to `requirements.txt`
  - Files: `requirements.txt`, `.gitignore`, `package.json`, `scripts/start_all.js`

### 2026-01-21
- **Implemented Persistent AI Response Cache** - SQLite-backed caching for instant repeated queries
  - **Database**: Added `response_cache` table to `metadata.db` with query/context hashing
  - **Logic**: Implemented `compute_cache_key`, `cached_smart_summary`, `cached_generate_ai_answer`
  - **Performance**: Added model warmup on startup (background thread) to eliminate first-query delay
  - **UI**: Added "AI Response Cache" stats and "Clear Cache" button in Settings
  - **Endpoints**: Added `/api/cache/stats` and `/api/cache/clear`
  - Files: `backend/database.py`, `backend/llm_integration.py`, `backend/api.py`, `frontend/src/components/SettingsModal.jsx`
  - Tests: `backend/tests/test_cache.py` (New)
- **Reorganized project into clean folder structure** - Better separation of concerns
  - `backend/`: All Python modules (api.py, database.py, indexing.py, etc.)
  - `backend/tests/`: All pytest tests (moved from root tests/)
  - `scripts/`: Utility scripts (run_tests.py, benchmark_models.py, start_all.js)
  - `data/`: Generated files (index.faiss, metadata.db, benchmark_results.json)
  - Updated all imports to use absolute `backend.` module prefix
  - `package.json`: Updated scripts to use new paths (backend.api:app)
  - `scripts/start_all.js`: Updated uvicorn command
  - `scripts/run_tests.py`: Updated test discovery paths
  - `AGENTS.md`: Updated project structure documentation
- **Expanded model library for 32GB RAM systems** - Added 14 new model options
- **Fixed LLM model loading error** - Diagnosed why "Local model failed to load" appeared
  - Root cause: llama-2-7b and mistral-7b models corrupted/incompatible with llama_cpp version
  - `config.ini`: Changed model_path from llama-2-7b to phi-2.Q4_K_M.gguf (working model)
  - Created `test_models_quick.py` and `test_quality.py` for model diagnostics
  - 2/4 models work: TinyLlama (fast, 4.1s) and Phi-2 (quality, 8.7s)
- **Renamed "Nexus AI Insight" to "AI Insights"** in UI
  - `frontend/src/components/SearchResults.jsx`: Updated title text
- **Removed corrupted model files** - Deleted llama-2-7b-chat.Q4_K_M.gguf and mistral-7b-instruct-v0.1.Q4_K_M.gguf
- **Added agent skills for file processing** - Created 4 document processing skills
  - `.agent/skills/pdf/SKILL.md`, `.agent/skills/docx/SKILL.md`
  - `.agent/skills/xlsx/SKILL.md`, `.agent/skills/pptx/SKILL.md`
  - Added `Agent Skills` section to `AGENTS.md` referencing these files
  - Updated `.gitignore` to exclude `.agent/skills/`
- **Improved Folder Management** - Solved "re-add folders" issue
  - Added "Recent Folders" history dropdown in Settings
  - Implemented auto-save when adding/removing folders
  - Added `folder_history` table to `metadata.db` with migration from existing files
  - `backend/database.py`, `backend/api.py`, `frontend/src/components/SettingsModal.jsx`
- **Fixed test data leaking into folder history** - Test isolation fix
  - Added `delete_folder_history_item()` and `clear_folder_history()` to `database.py`
  - Added DELETE endpoints `/api/folders/history` and `/api/folders/history/item`
  - Updated `test_database.py` to use module-level database setup for proper isolation
  - Added "Clear All" button and individual delete buttons to folder history dropdown in Settings UI
  - Files: `backend/database.py`, `backend/api.py`, `backend/tests/test_database.py`, `frontend/src/components/SettingsModal.jsx`
- **Fixed File Locks** - Database initialization moved to startup event to prevent lock issues during tests

### 2026-01-21 (Part 2)
- **Restored 100% Test Coverage** - Added tests for new RAPTOR DB functions
  - `backend/tests/test_raptor_clusters.py`: Covered `add_cluster`, `get_clusters_by_level`, `clear_clusters`
- **Created "Golden Dataset" for robust testing** - Mixed Stategy (Synthetic + Real)
  - `scripts/create_golden_dataset.py`: Python script to generate synthetic PDF/DOCX/PPTX/XLSX handling diverse topics (Nature, Business, Sales) and download real-world samples.
  - `scripts/verify_golden_set.py`: Automated verification script that indexes the golden set and asserts specific factual retrieval ("needle in haystack").
  - `data/golden_dataset/`: Target directory for test files.
  - Added documentation to `AGENTS.md`.

### 2026-01-30
- **Optimized Startup** - Reduced polling interval to 500ms and enabled early browser launch
  - Files: `scripts/start_all.js`
  - Verification: Manual user verification required (restart app)
- **Backend Connection Resilience** - Added retry logic to Frontend to handle race conditions during fast startup
  - Files: `frontend/src/App.jsx`
  - Verification: Manual verification (Frontend should eventually load even if backend is slow)
- **Robust Port Cleanup** - Startup script now aggressively kills zombie processes on ports 8000/5173
  - Files: `scripts/start_all.js`
  - Verification: Manual verification (Ctrl+C and restart should work immediately)

### 2026-01-09
- **Enhanced LLM output quality** - AI now references filenames and quotes specific content
  - `llm_integration.py`: Added `file_name` param to `smart_summary()`, improved prompts to request specific details
  - `api.py`: Pass file context to LLM functions, prepend `[From: filename]` to context snippets
- **Refined API & Tests** - Fixed issues with model deletion and search history endpoints
  - `api.py`: Refactored `delete_model` to use `model_manager` and fixed history delete response
  - `tests/test_api.py`, `tests/test_config_and_edge_cases.py`: Updated to match plural `folders` config and fixed `TestClient` compatibility
- **Added 100% test coverage** - 93 frontend + 101 backend tests
  - `tests/test_api.py`, `test_database.py`, `test_llm_integration_full.py`, `test_indexing.py`, `test_config_and_edge_cases.py`
  - `frontend/src/test/SearchBar.test.jsx`, `SearchResults.test.jsx`, `SettingsModal.test.jsx`, `ModelManager.test.jsx`
- **Created AGENTS.md** - Workspace instructions

### 2026-02-02
- **Integrated Sentinel Security Fixes (Branch 3)**
  - **feat**: Merged `sentinel-model-manager-fix` which generalizes path validation logic (`is_safe_path`).
  - **fix**: Resolved conflict in `backend/model_manager.py` adopting the more robust security check.
  - **Files**: `backend/model_manager.py`
  - **Verification**: Tests passed on branch before merge.

### 2026-02-01
- **Security Fix: Arbitrary File Deletion in Model Manager**
  - **fix**: Patched `delete_model` in `backend/model_manager.py` to use `is_safe_path` validation, preventing path traversal attacks.
  - **test**: Added comprehensive security tests in `backend/tests/test_security_fix.py`.
  - **Files**: `backend/model_manager.py`, `backend/tests/test_security_fix.py`

### Entry Template
```
### YYYY-MM-DD
- **What changed** - Brief description
  - Files: modified files list
```

> **Always read [AGENTS.md](cci:7://file:///c:/Users/siddh/OneDrive/Desktop/Projects/File-Search-Engine-1/AGENTS.md:0:0-0:0) in project root for the latest Change Log before and after making changes.**