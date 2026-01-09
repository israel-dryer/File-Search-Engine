---
trigger: always_on
---

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
├── api.py              # FastAPI endpoints (main entry)
├── database.py         # SQLite CRUD operations
├── indexing.py         # FAISS index creation
├── search.py           # Semantic search logic
├── file_processing.py  # Text extraction (PDF, DOCX, XLSX, PPTX, TXT)
├── llm_integration.py  # LLM provider abstraction
├── model_manager.py    # GGUF model downloads
├── tests/              # pytest tests
│   ├── test_api.py, test_database.py, test_search.py
│   ├── test_indexing.py, test_file_processing.py
│   └── test_llm_integration_full.py
├── frontend/src/
│   ├── App.jsx         # Main component (holds global state)
│   ├── components/     # UI components
│   │   ├── Header.jsx, SearchBar.jsx, SearchResults.jsx
│   │   ├── SettingsModal.jsx, ModelManager.jsx
│   │   └── SearchHistory.jsx, FileList.jsx, BenchmarkResults.jsx
│   └── test/           # Vitest tests
├── models/             # Downloaded GGUF models
├── config.ini          # User configuration
├── index.faiss         # Vector embeddings (generated)
└── metadata.db         # SQLite database (generated)
```

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

## Mandatory Rules

1. **Run tests before AND after changes** - `npm run test`
2. **Mock all LLM calls** in tests to avoid costs
3. **Frontend uses Vitest** - import from 'vitest', not jest
4. **Check existing patterns** before implementing
5. **Update Change Log** after every modification

---

## Change Log

> **CRITICAL: Add entry here after EVERY change with date, description, and files.**

### 2026-01-09
- **Added 100% test coverage** - 93 frontend + 65 backend tests
  - `tests/test_api.py`, `test_database.py`, `test_llm_integration_full.py`
  - `frontend/src/test/SearchBar.test.jsx`, `SearchResults.test.jsx`, `SettingsModal.test.jsx`, `ModelManager.test.jsx`
- **Created AGENTS.md** - Workspace instructions

### Entry Template
```
### YYYY-MM-DD
- **What changed** - Brief description
  - Files: modified files list
```

> **Always read [AGENTS.md](cci:7://file:///c:/Users/siddh/OneDrive/Desktop/Projects/File-Search-Engine-1/AGENTS.md:0:0-0:0) in project root for the latest Change Log before and after making changes.**