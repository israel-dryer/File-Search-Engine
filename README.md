# File Search Engine - AI-Powered Local Document Search

An intelligent, semantic search engine for your local documents powered by AI embeddings and large language models. Search across PDFs, Word documents, Excel spreadsheets, PowerPoint presentations, and text files using natural language queries.

![Project Status](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![React](https://img.shields.io/badge/react-18+-61DAFB.svg)

## 🌟 Features

- **🔍 Semantic Search**: Find documents using natural language, not just keywords
- **📂 Multiple File Types**: Supports PDF, DOCX, XLSX, PPTX, and TXT files
- **🤖 AI Summaries**: Get instant AI-generated summaries of search results
- **🏠 Fully Local**: Use open-source GGUF models - no API keys required!
- **☁️ Cloud Option**: Optional OpenAI API integration for enhanced performance
- **📊 Metadata Tracking**: SQLite database tracks files, sizes, dates, and indexing stats
- **📜 Search History**: View and re-run previous searches
- **🎨 Modern UI**: Beautiful, responsive dark/light mode interface
- **⬇️ Model Manager**: Download and manage open-source LLM models directly in the app
- **💾 Persistent Storage**: Indexed data saved between sessions

## 🏗️ Architecture

### Tech Stack

**Backend**:
- FastAPI - Modern Python web framework
- FAISS - Facebook's vector similarity search
- LangChain - LLM integration framework
- SQLite - Metadata and history storage
- LlamaCpp - Local model inference
- OpenAI API (optional) - Cloud embeddings

**Frontend**:
- React 18 - UI framework
- Vite - Lightning-fast build tool
- TailwindCSS - Utility-first styling
- Axios - HTTP client
- Lucide Icons - Beautiful icons

### Data Flow

```
User selects folder → Extract text from files → Split into chunks (1000 chars)
     ↓
Generate embeddings (Local/OpenAI) → Store in FAISS index + SQLite metadata
     ↓
User searches → Generate query embedding → Find similar documents → Return results with AI summaries
```

### Storage

1. **`index.faiss`** - Vector embeddings for similarity search
2. **`index_docs.pkl`** - Document text chunks
3. **`index_tags.pkl`** - AI-generated tags
4. **`metadata.db`** - SQLite database:
   - File metadata (path, size, modified date, chunks)
   - Search history (queries, timing, result counts)
   - User preferences
5. **`models/`** - Downloaded local LLM models (GGUF format)

## 📋 Prerequisites

- **Python 3.8+**
- **Node.js 16+**
- **8GB+ RAM** (for local models)
- **OpenAI API Key** (optional, for cloud mode)

## 🚀 Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/yourusername/File-Search-Engine
cd File-Search-Engine-1

# Install all dependencies (backend + frontend + tools)
npm run install-all

# Or manually:
pip install -r requirements.txt
cd frontend && npm install && cd ..
```

### 2. Start the Application (Single Command!)

```bash
npm run start
```

This will:
- ✅ Check port availability (8000, 5173)
- ✅ Start the FastAPI backend
- ✅ Start the Vite frontend
- ✅ Open your browser automatically

**Alternative (Manual Start):**
```bash
# Terminal 1: Backend
uvicorn api:app --reload

# Terminal 2: Frontend
cd frontend && npm run dev
```

**Available Scripts:**
| Command | Description |
|---------|-------------|
| `npm run start` | Start backend + frontend together |
| `npm run benchmark` | Run model performance benchmarks |
| `npm run test` | Run all unit tests |

## 🧪 Testing

All tests are in `tests/`. **Always run tests before committing changes.**

### Quick Start

```bash
npm run test          # Fast unit tests (~12 seconds) - run before every commit
npm run test:full     # All tests including model tests (~5-10 minutes)
npm run test:stress   # Performance stress tests
```

### Types of Tests Explained

| Type | What It Does | When to Run |
|------|--------------|-------------|
| **Unit Tests** | Tests individual functions (API, database, search, etc.) in isolation | Before every commit |
| **Model Tests** | Tests LLM loading, text generation, model comparison | When changing model code |
| **Stress Tests** | Simulates heavy usage - many concurrent requests | Before releases |
| **Coverage** | Shows which lines of code are tested vs untested | To improve test quality |

### Commands Quick Reference

| Command | Description | Speed |
|---------|-------------|-------|
| `npm run test` | Quick unit tests | ~12 sec |
| `npm run test:full` | All tests (incl. model) | ~10 min |
| `npm run test:stress` | Load/stress tests | ~2 min |
| `python run_tests.py --coverage` | With coverage report | ~15 sec |

### What is Coverage?

**Coverage** shows the percentage of your code that is tested. Higher coverage = more confidence.

```bash
# Run with coverage (needs pytest-cov: pip install pytest-cov)
python run_tests.py --coverage
```

This generates a report showing which lines have tests and which don't.

### What is Stress Testing?

**Stress tests** simulate real-world heavy usage:
- Many search queries at once
- Large file indexing
- Concurrent API requests

This helps find performance bottlenecks and memory leaks.

```bash
python tests/stress_test.py
```

### Test Files Overview

| File | Tests |
|------|-------|
| `test_api.py` | API endpoints (search, config, index) |
| `test_database.py` | File metadata, search history storage |
| `test_file_processing.py` | PDF, DOCX, XLSX, PPTX extraction |
| `test_search.py` | FAISS semantic search |
| `test_model_comparison.py` | Model ranking by accuracy/speed |
| `stress_test.py` | Load testing, concurrent requests |


## 💡 Usage Guide

### First-Time Setup

1. **Open the app** at `http://localhost:5173`

2. **Download a Local Model** (Recommended):
   - Click the ⚙️ Settings icon
   - Select **"Local (GGUF)"** provider
   - In the Model Manager, click **Download** on:
     - **TinyLlama 1.1B** (637 MB) - Fast, good for testing
     - **Phi-2 2.7B** (1.7 GB) - Better quality
     - **Mistral 7B** (4.37 GB) - Best quality (requires 16GB+ RAM)
   - Wait for download to complete (progress shown)
   - Click **Select** to activate the model

3. **Configure Folder**:
   - Enter the absolute path to your documents folder
   - Example: `C:\Users\YourName\Documents\Papers`
   - Click **Save Changes**

4. **Index Your Files**:
   - Click **"Index Now"** button
   - Watch the backend console for progress
   - Indexing time depends on folder size (expect ~30 seconds for 100 files)

5. **Start Searching**:
   - Type natural language queries (e.g., "machine learning papers about transformers")
   - View results with AI summaries and tags
   - Click on search history to re-run queries

### Alternative: Using OpenAI API

If you prefer cloud-based embeddings:

1. Get an API key from [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Settings → Keep or select **"OpenAI"** provider
3. Enter your API key
4. Save and index

**Note**: OpenAI provides higher quality embeddings but incurs API costs.

## 📁 Supported File Types

| Type | Extensions | Features |
|------|-----------|----------|
| **Documents** | `.pdf`, `.docx`, `.txt` | Full text extraction |
| **Spreadsheets** | `.xlsx` | Cell content extraction from all sheets |
| **Presentations** | `.pptx` | Slide text and shape extraction |

### File Processing Details

- **PDF**: PyPDF extracts text from all pages
- **Word**: python-docx extracts paragraph text
- **Excel**: openpyxl extracts cell values
- **PowerPoint**: python-pptx extracts slide text
- **Text**: UTF-8 with error handling

**Limitations**:
- Scanned PDFs without OCR won't extract text
- Image-heavy presentations may have limited text
- Password-protected files not supported

## 🔧 API Endpoints

### Configuration
- `GET /api/config` - Get current settings
- `POST /api/config` - Update settings

### Indexing
- `POST /api/index` - Start background indexing
- `GET /api/files` - List indexed files with metadata

### Search
- `POST /api/search` - Semantic search with AI summaries
- `GET /api/search/history` - Recent search history

### Models
- `GET /api/models/available` - Downloadable models list (with RAM requirements)
- `GET /api/models/local` - Downloaded models
- `POST /api/models/download/{model_id}` - Start download (with resource validation)
- `GET /api/models/status` - Download progress

### Benchmarks
- `POST /api/benchmarks/run` - Start performance benchmark suite
- `GET /api/benchmarks/status` - Check benchmark progress
- `GET /api/benchmarks/results` - Get latest benchmark results

## 📊 Model Selection Guide

| Model | Size | RAM | Speed | Quality | Best For |
|-------|------|-----|-------|---------|----------|
| **TinyLlama 1.1B** ⭐ | 637 MB | 2 GB | ⚡⚡⚡ | ⭐⭐ | Testing, older hardware |
| **Gemma 2B** ⭐ | 1.5 GB | 4 GB | ⚡⚡⚡ | ⭐⭐⭐ | Fast summarization |
| **Phi-2 2.7B** ⭐ | 1.7 GB | 5 GB | ⚡⚡ | ⭐⭐⭐ | Reasoning, code |
| **Phi-3 Mini** ⭐ | 2.2 GB | 6 GB | ⚡⚡ | ⭐⭐⭐⭐ | General purpose |
| **Mistral 7B** ⭐ | 4.4 GB | 8 GB | ⚡ | ⭐⭐⭐⭐⭐ | Best quality |
| **Llama 2 7B** | 4.1 GB | 8 GB | ⚡ | ⭐⭐⭐⭐ | Chat, general |
| **Qwen 1.5 7B** | 4.4 GB | 8 GB | ⚡ | ⭐⭐⭐⭐ | Multilingual |

⭐ = Recommended models

### Running Benchmarks

Compare model performance with the built-in benchmark suite:

```bash
# Run from command line
npm run benchmark

# Or via API
curl -X POST http://localhost:8000/api/benchmarks/run
```

Benchmarks measure:
- **Tokens per second (TPS)** - Generation speed
- **Fact retention** - Accuracy of summaries
- **Memory usage** - RAM consumption
- **Load time** - Model startup time

Results are saved to `benchmark_results.md` and viewable in the Settings panel.


## 🧪 Testing

### Automated Tests

Run the comprehensive workflow test:

```bash
python test_workflow.py
```

This verifies:
- ✅ File detection and extraction
- ✅ Database operations
- ✅ Model manager functionality
- ✅ Configuration loading

### Manual Testing Checklist

**Setup & Configuration**
- [ ] Backend starts without errors
- [ ] Frontend loads properly
- [ ] Can open Settings modal
- [ ] Folder path validation works

**Model Management**
- [ ] Can view available models
- [ ] Download progress updates in real-time
- [ ] Can select downloaded model
- [ ] Model file appears in `models/` directory

**Indexing**
- [ ] Indexing starts when clicking "Index Now"
- [ ] Progress shown in backend console
- [ ] Files listed in `/api/files` endpoint
- [ ] `.faiss` and `.pkl` files created
- [ ] Metadata stored in `metadata.db`

**Search**
- [ ] Can enter search queries
- [ ] Results appear with summaries
- [ ] Tags displayed correctly
- [ ] Search history saved
- [ ] Can re-run searches from history

## 🛠️ Troubleshooting

### "Index not loaded" error

**Cause**: No files have been indexed yet.

**Solution**:
1. Go to Settings
2. Enter a valid folder path
3. Click "Index Now"
4. Wait for console to show "Indexing completed successfully"

### Indexing fails with "Model path required"

**Cause**: Using Local provider without selecting a model.

**Solution**:
1. Settings → Local LLM → Model Manager
2. Download a model (TinyLlama recommended)
3. Click "Select" on the downloaded model
4. Try indexing again

### Model download stuck or failed

**Cause**: Network interruption or timeout.

**Solutions**:
- Refresh the page and try again
- Check internet connection
- Try a smaller model first (TinyLlama)
- Download models manually to `models/` folder

### Search returns no results

**Causes & Solutions**:
- **Query too specific**: Try broader terms
- **No matching content**: Verify files were indexed (`/api/files`)
- **Index corrupted**: Delete `.faiss` and `.pkl` files, re-index

### Out of memory error with large models

**Cause**: Insufficient RAM for the selected model.

**Solutions**:
- Use TinyLlama (requires ~2GB RAM)
- Close other applications
- Upgrade RAM or use OpenAI API instead

## 📂 Project Structure

```
File-Search-Engine-1/
├── api.py                    # FastAPI server & endpoints
├── database.py               # SQLite operations
├── indexing.py               # FAISS indexing logic
├── search.py                 # Semantic search
├── file_processing.py        # Text extraction
├── llm_integration.py        # LLM provider abstraction
├── model_manager.py          # Model downloads
├── test_workflow.py          # Automated tests
├── test_extraction.py        # File extraction test
├── requirements.txt          # Python dependencies
├── config.ini                # User configuration
├── metadata.db               # SQLite database
├── index.faiss               # Vector index
├── models/                   # Downloaded models
└── frontend/
    ├── src/
    │   ├── App.jsx                # Main component
    │   ├── components/
    │   │   ├── Header.jsx         # Navigation
    │   │   ├── SearchBar.jsx      # Search input
    │   │   ├── SearchResults.jsx  # Results display
    │   │   ├── SettingsModal.jsx  # Configuration
    │   │   ├── ModelManager.jsx   # Model downloads
    │   │   ├── FileList.jsx       # Indexed files
    │   │   └── SearchHistory.jsx  # Recent searches
    │   └── lib/utils.js           # Utilities
    └── package.json               # Node dependencies
```

## 🔮 Future Enhancements

- [ ] Incremental indexing (only new/modified files)
- [ ] Real-time UI progress for indexing
- [ ] File preview in results
- [ ] Export search results to CSV/JSON
- [ ] Document relationships graph
- [ ] OCR for scanned PDFs
- [ ] Multi-language support
- [ ] Collaborative features

## ⚠️ Known Limitations

1. **Folder Selection**: Manual path entry only (browser folder picker doesn't work through web interface)
2. **Large Files**: Files over 100MB may slow indexing significantly
3. **Model Size**: Local 7B models require 16GB+ RAM
4. **First Index**: Initial indexing can be slow (especially with local models)

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/File-Search-Engine/issues)
- **Docs**: See `README.md` and inline code comments
- **Tests**: Run `python test_workflow.py` for diagnostics

---

**Built with ❤️ using FastAPI, React, FAISS, and LlamaCpp**

**Ready to search smarter, not harder!** 🚀
