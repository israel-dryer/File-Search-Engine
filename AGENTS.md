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

---

## Change Log

> **CRITICAL: Add entry here after EVERY change with date, description, and files.**

### 2026-01-21
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

### 2026-01-21
- **Implemented Persistent AI Response Cache** - SQLite-backed caching for instant repeated queries
  - **Database**: Added `response_cache` table to `metadata.db` with query/context hashing
  - **Logic**: Implemented `compute_cache_key`, `cached_smart_summary`, `cached_generate_ai_answer`
  - **Performance**: Added model warmup on startup to eliminate first-query delay
  - **Endpoints**: Added `/api/cache/stats` and `/api/cache/clear`
  - Files: `backend/database.py`, `backend/llm_integration.py`, `backend/api.py`
  - Tests: `backend/tests/test_cache.py` (New)
- **Folder Restructure Complete** - Backend files moved to `backend/`, scripts to `scripts/`, data to `data/`
- **Updated Imports** - All modules now use absolute `backend.` imports
- **Fixed File Locks** - Database initialization moved to startup event to prevent lock issues during tests
- Files: `backend/*`, `scripts/*`, `package.json`, `AGENTS.md`

### Entry Template
```
### YYYY-MM-DD
- **What changed** - Brief description
  - Files: modified files list
```

> **Always read [AGENTS.md](cci:7://file:///c:/Users/siddh/OneDrive/Desktop/Projects/File-Search-Engine-1/AGENTS.md:0:0-0:0) in project root for the latest Change Log before and after making changes.**