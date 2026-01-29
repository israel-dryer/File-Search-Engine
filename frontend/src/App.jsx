import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import SearchBar from './components/SearchBar';
import SearchResults from './components/SearchResults';
import SearchHistory from './components/SearchHistory';
import SettingsModal from './components/SettingsModal';
import AgentChat from './components/AgentChat';
import CosmicBackground from './components/CosmicBackground';
import axios from 'axios';
import { History } from 'lucide-react';

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
    const [isAgentMode, setIsAgentMode] = useState(false);
    const [agentQuery, setAgentQuery] = useState("");

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
        fetchModels();
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
        const selectedModel = availableModels.find(m => m.name.replace('.gguf', '') === modelName || m.name === modelName);
        const modelPath = selectedModel ? selectedModel.path : "";

        try {
            const currentConfig = await axios.get('http://localhost:8000/api/config');
            await axios.post('http://localhost:8000/api/config', {
                folders: currentConfig.data.folders || [],
                auto_index: currentConfig.data.auto_index,
                openai_api_key: currentConfig.data.openai_api_key,
                provider: 'local',
                local_model_path: modelPath
            });
            setActiveModel(modelName);
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
        setHasSearched(true);
        setIsHistoryOpen(false);

        if (isAgentMode) {
            setAgentQuery(query);
            return;
        }

        setIsLoading(true);
        setAiAnswer("");
        setSearchResults([]);

        try {
            // Stage 1: Get File List (Fast)
            const response = await axios.post('http://localhost:8000/api/search', { query });
            const results = response.data.results || response.data;
            setSearchResults(results);

            if (response.data.active_model) {
                const modelName = response.data.active_model.replace('.gguf', '');
                setActiveModel(modelName);
            }

            setIsLoading(false); // Show results immediately

            // Stage 2: Stream AI Answer (Slow)
            if (results.length > 0) {
                setAiAnswer("Thinking...");

                try {
                    const streamResponse = await fetch('http://localhost:8000/api/stream-answer', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ query })
                    });

                    if (streamResponse.body) {
                        const reader = streamResponse.body.getReader();
                        const decoder = new TextDecoder();
                        let accumulatedAnswer = "";
                        let isFirstChunk = true;

                        while (true) {
                            const { done, value } = await reader.read();
                            if (done) break;

                            const chunk = decoder.decode(value, { stream: true });

                            if (isFirstChunk) {
                                accumulatedAnswer = "";
                                isFirstChunk = false;
                            }

                            accumulatedAnswer += chunk;
                            setAiAnswer(accumulatedAnswer);
                        }
                    }
                } catch (streamError) {
                    console.error("Streaming failed:", streamError);
                    setAiAnswer(""); // Clear if failed
                }
            }
        } catch (error) {
            console.error('Search failed:', error);
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen text-foreground selection:bg-primary/20 relative">
            <CosmicBackground />
            <Header
                darkMode={darkMode}
                toggleDarkMode={() => setDarkMode(!darkMode)}
                openSettings={() => setIsSettingsOpen(true)}
                toggleHistory={() => setIsHistoryOpen(!isHistoryOpen)}
                isHistoryOpen={isHistoryOpen}
                activeModel={activeModel}
                availableModels={availableModels}
                onModelChange={handleModelChange}
                indexingStatus={indexingStatus}
            />

            <SearchHistory
                isOpen={isHistoryOpen}
                onClose={() => setIsHistoryOpen(false)}
                onSelectQuery={handleSearch}
                isMobile={isMobile}
            />

            <main className={`relative z-10 container mx-auto pb-16 min-h-[calc(100vh-3.5rem)] flex flex-col transition-all duration-300 ease-in-out ${isHistoryOpen && !isMobile ? 'pl-72' : ''}`}>
                <div className={`flex-1 flex flex-col items-center w-full max-w-3xl mx-auto px-4 ${hasSearched ? 'pt-8' : 'justify-center'}`}>

                    {!hasSearched && (
                        <div className="text-center space-y-4 mb-12">
                            <h1 className="text-4xl md:text-5xl font-bold tracking-tight">File Search</h1>
                            <p className="text-muted-foreground text-lg md:text-xl max-w-2xl mx-auto">
                                Your universal file search engine.
                            </p>
                        </div>
                    )}

                    <div className="w-full">
                        <SearchBar
                            onSearch={handleSearch}
                            isLoading={isLoading}
                            isAgentMode={isAgentMode}
                            onToggleAgent={() => setIsAgentMode(!isAgentMode)}
                        />
                    </div>

                    {isAgentMode && agentQuery ? (
                        <AgentChat query={agentQuery} />
                    ) : (
                        <SearchResults results={searchResults} aiAnswer={aiAnswer} />
                    )}
                </div>
            </main>

            <SettingsModal
                isOpen={isSettingsOpen}
                onClose={() => setIsSettingsOpen(false)}
                onSave={() => { checkConfig(); fetchModels(); }}
                activeModel={activeModel}
            />
        </div>
    );
}

export default App;