import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import SearchBar from './components/SearchBar';
import SearchResults from './components/SearchResults';
import SearchHistory from './components/SearchHistory';
import SettingsModal from './components/SettingsModal';
import axios from 'axios';
import { History, Sparkles } from 'lucide-react';

function App() {
    const [darkMode, setDarkMode] = useState(true);
    const [isSettingsOpen, setIsSettingsOpen] = useState(false);
    const [isHistoryOpen, setIsHistoryOpen] = useState(false);
    const [searchResults, setSearchResults] = useState([]);
    const [aiAnswer, setAiAnswer] = useState("");
    const [activeModel, setActiveModel] = useState(null);
    const [availableModels, setAvailableModels] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [hasSearched, setHasSearched] = useState(false);
    const [isMobile, setIsMobile] = useState(window.innerWidth < 768);
    const [folders, setFolders] = useState([]);
    const [indexingStatus, setIndexingStatus] = useState({ running: false, progress: 0 });

    useEffect(() => {
        const handleResize = () => setIsMobile(window.innerWidth < 768);
        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, []);

    useEffect(() => {
        let interval;
        const fetchStatus = async () => {
            try {
                const res = await axios.get('http://localhost:8000/api/index/status');
                setIndexingStatus(res.data);
                if (!res.data.running) clearInterval(interval);
            } catch (e) {
                console.error("Status check failed", e);
            }
        };

        if (indexingStatus.running) {
            interval = setInterval(fetchStatus, 2000);
        }
        return () => clearInterval(interval);
    }, [indexingStatus.running]);

    useEffect(() => {
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            setDarkMode(savedTheme === 'dark');
        } else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
            setDarkMode(true);
        }
        checkConfig();
        fetchModels(); // [NEW]
    }, []);

    const fetchModels = async () => {
        try {
            const res = await axios.get('http://localhost:8000/api/models/local');
            if (Array.isArray(res.data)) {
                setAvailableModels(res.data);
            }
        } catch (error) {
            console.error("Failed to fetch local models", error);
        }
    };

    const checkConfig = async () => {
        try {
            const response = await axios.get('http://localhost:8000/api/config');
            setFolders(response.data.folders || []);
            if (response.data.local_model_path) {
                const modelName = response.data.local_model_path.split('\\').pop().split('/').pop().replace('.gguf', '');
                setActiveModel(modelName);
            } else {
                setActiveModel("Default Embeddings");
            }
        } catch (error) {
            console.error("Failed to check config", error);
        }
    };

    const handleModelChange = async (modelName) => {
        // Find the full path from availableModels
        const selectedModel = availableModels.find(m => m.name.replace('.gguf', '') === modelName || m.name === modelName);
        const modelPath = selectedModel ? selectedModel.path : "";

        try {
            // Get current config to preserve other settings
            const currentConfig = await axios.get('http://localhost:8000/api/config');

            await axios.post('http://localhost:8000/api/config', {
                folders: currentConfig.data.folders || [],
                auto_index: currentConfig.data.auto_index,
                openai_api_key: currentConfig.data.openai_api_key,
                provider: 'local',
                local_model_path: modelPath
            });
            setActiveModel(modelName);
            console.log(`Switched to model: ${modelName} (${modelPath})`);
        } catch (error) {
            console.error("Failed to switch model", error);
        }
    };

    useEffect(() => {
        if (darkMode) {
            document.documentElement.classList.add('dark');
            localStorage.setItem('theme', 'dark');
        } else {
            document.documentElement.classList.remove('dark');
            localStorage.setItem('theme', 'light');
        }
    }, [darkMode]);

    const handleSearch = async (query) => {
        setIsLoading(true);
        setHasSearched(true);
        setIsHistoryOpen(false);
        setAiAnswer(""); // Reset previous answer
        setSearchResults([]); // Clear previous results
        try {
            const response = await axios.post('http://localhost:8000/api/search', { query });
            setSearchResults(response.data.results || response.data);
            if (response.data.ai_answer) {
                setAiAnswer(response.data.ai_answer);
            }
            if (response.data.active_model) {
                setActiveModel(response.data.active_model);
            }
        } catch (error) {
            console.error('Search failed:', error);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-background text-foreground selection:bg-primary/20 transition-colors duration-500 relative">
            {/* 3D Background Image Layer */}
            <div className="fixed inset-0 z-[-2] bg-cover bg-center bg-no-repeat opacity-20 dark:opacity-10 transition-opacity duration-1000"
                style={{ backgroundImage: 'url("https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2672&auto=format&fit=crop")' }}>
                <div className="absolute inset-0 bg-background/80 backdrop-blur-[2px]" />
            </div>

            {/* 3D Floating Elements */}
            <div className="fixed inset-0 overflow-hidden -z-10 pointer-events-none">
                <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary/10 rounded-full blur-[120px] animate-float" />
                <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-blue-600/10 rounded-full blur-[120px] animate-float" style={{ animationDelay: '-2s' }} />
            </div>

            <Header
                darkMode={darkMode}
                toggleDarkMode={() => setDarkMode(!darkMode)}
                openSettings={() => setIsSettingsOpen(true)}
                activeModel={activeModel}
                availableModels={availableModels}
                onModelChange={handleModelChange}
                indexingStatus={indexingStatus}
            />

            {/* 3D Floating History Button - Responsive adaptation */}
            <button
                onClick={() => setIsHistoryOpen(!isHistoryOpen)}
                className={`fixed left-4 ${hasSearched ? 'top-20' : 'bottom-10'} z-20 p-3 rounded-2xl glass-v2 transition-all duration-300 transform border border-white/20 hover:scale-110 active:scale-95 shadow-2xl ${isHistoryOpen ? 'rotate-12 translate-x-1' : ''}`}
                title="Search History"
            >
                <History className="w-5 h-5 text-primary" />
            </button>

            <SearchHistory
                isOpen={isHistoryOpen}
                onClose={() => setIsHistoryOpen(false)}
                onSelectQuery={handleSearch}
                isMobile={isMobile}
            />

            <main className={`container mx-auto pb-16 min-h-[calc(100vh-3.5rem)] flex flex-col transition-all duration-500 ease-in-out ${isHistoryOpen && !isMobile ? 'pl-72' : ''}`}>
                <div className={`flex-1 flex flex-col items-center w-full max-w-5xl mx-auto px-4 ${hasSearched ? 'pt-8' : 'justify-center'}`}>

                    {/* 3D Hero Section */}
                    {!hasSearched && (
                        <div className="text-center space-y-8 animate-slide-up mb-12">
                            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-2xl glass-v2 mb-4 animate-float">
                                <Sparkles className="w-4 h-4 text-primary" />
                                <span className="text-sm font-semibold tracking-wide uppercase">Hyper-Search Engine</span>
                            </div>

                            <h1 className="text-3d text-5xl md:text-7xl lg:text-8xl tracking-tighter leading-[0.9] py-4 bg-clip-text">
                                EXPLORE<br />
                                YOUR DATA
                            </h1>

                            <p className="text-muted-foreground text-lg md:text-xl max-w-2xl mx-auto font-medium opacity-80">
                                Navigate your local filesystem with 3D physical search technology and AI intelligence.
                            </p>
                        </div>
                    )}

                    <div className={`w-full transition-all duration-500 ${hasSearched ? '' : 'animate-float'}`} style={{ animationDelay: '0.5s' }}>
                        <SearchBar onSearch={handleSearch} isLoading={isLoading} />
                    </div>

                    <SearchResults results={searchResults} aiAnswer={aiAnswer} />
                </div>
            </main>

            <SettingsModal
                isOpen={isSettingsOpen}
                onClose={() => setIsSettingsOpen(false)}
                onSave={() => { checkConfig(); fetchModels(); }}
            />
        </div>
    );
}

export default App;
