import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { X, Settings, FolderOpen, Loader2, Save, ChevronDown, ChevronUp, Key, Cpu, Trash2, CheckCircle2 } from 'lucide-react';
import ModelManager from './ModelManager';

const SettingsModal = ({ isOpen, onClose, onSave, activeModel }) => {
    const [config, setConfig] = useState({
        folders: [],
        auto_index: false,
        provider: 'local',
        // API Keys for different providers
        openai_api_key: '',
        gemini_api_key: '',
        anthropic_api_key: '',
        grok_api_key: '',
        // Local model settings
        local_model_path: '',
        local_model_type: 'llamacpp'
    });
    const [isLoading, setIsLoading] = useState(false);
    const [indexingStatus, setIndexingStatus] = useState({
        running: false,
        progress: 0,
        current_file: '',
        total_files: 0,
        processed_files: 0
    });
    const [expandedSection, setExpandedSection] = useState(null);
    const [folderHistory, setFolderHistory] = useState([]);
    const [showHistory, setShowHistory] = useState(false);
    const [cacheStats, setCacheStats] = useState({ total_entries: 0, total_hits: 0 });

    useEffect(() => {
        if (isOpen) {
            fetchConfig();
        }
    }, [isOpen]);

    useEffect(() => {
        let interval;
        if (isOpen) {
            fetchIndexingStatus();
            interval = setInterval(fetchIndexingStatus, 1500);
        }
        return () => clearInterval(interval);
    }, [isOpen]);

    useEffect(() => {
        if (isOpen) {
            fetchFolderHistory();
            fetchCacheStats();
        }
    }, [isOpen]);

    useEffect(() => {
        const handleKeyDown = (e) => {
            if (e.key === 'Escape' && isOpen) {
                onClose();
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [isOpen, onClose]);

    const fetchConfig = async () => {
        try {
            const response = await axios.get('http://localhost:8000/api/config');
            setConfig(prev => ({ ...prev, ...response.data }));
        } catch (error) {
            console.error('Failed to fetch config:', error);
        }
    };

    const fetchIndexingStatus = async () => {
        try {
            const response = await axios.get('http://localhost:8000/api/index/status');
            setIndexingStatus(response.data);
        } catch (error) {
            console.error('Failed to fetch status:', error);
        }
    };

    const fetchFolderHistory = async () => {
        try {
            const response = await axios.get('http://localhost:8000/api/folders/history');
            setFolderHistory(response.data || []);
        } catch (error) {
            console.error('Failed to fetch folder history:', error);
        }
    };

    const fetchCacheStats = async () => {
        try {
            const response = await axios.get('http://localhost:8000/api/cache/stats');
            setCacheStats(response.data);
        } catch (error) {
            console.error('Failed to fetch cache stats:', error);
        }
    };

    const handleSave = async () => {
        setIsLoading(true);
        try {
            await axios.post('http://localhost:8000/api/config', config);
            onSave();
            onClose();
        } catch (error) {
            console.error('Failed to save config:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const saveConfigData = async (newConfig) => {
        try {
            await axios.post('http://localhost:8000/api/config', newConfig);
            // Refresh history after save
            fetchFolderHistory();
        } catch (error) {
            console.error('Failed to save config:', error);
        }
    };

    const handleAddFolder = async () => {
        try {
            const response = await axios.get('http://localhost:8000/api/browse');
            if (response.data.folder && !config.folders.includes(response.data.folder)) {
                const newConfig = {
                    ...config,
                    folders: [...config.folders, response.data.folder]
                };
                setConfig(newConfig);
                await saveConfigData(newConfig);
            }
        } catch (error) {
            console.error('Failed to browse:', error);
        }
    };

    const handleAddFromHistory = async (folder) => {
        if (!config.folders.includes(folder)) {
            const newConfig = {
                ...config,
                folders: [...config.folders, folder]
            };
            setConfig(newConfig);
            await saveConfigData(newConfig);
            setShowHistory(false);
        }
    };

    const handleRemoveFolder = async (folderToRemove) => {
        const newConfig = {
            ...config,
            folders: config.folders.filter(f => f !== folderToRemove)
        };
        setConfig(newConfig);
        await saveConfigData(newConfig);
    };

    const handleRemoveFromHistory = async (folder, e) => {
        e.stopPropagation();  // Prevent adding the folder when clicking delete
        try {
            await axios.delete('http://localhost:8000/api/folders/history/item', {
                data: { path: folder }
            });
            fetchFolderHistory();  // Refresh the list
        } catch (error) {
            console.error('Failed to remove folder from history:', error);
        }
    };

    const handleClearAllHistory = async () => {
        if (confirm('Clear all folder history?')) {
            try {
                await axios.delete('http://localhost:8000/api/folders/history');
                setFolderHistory([]);
                setShowHistory(false);
            } catch (error) {
                console.error('Failed to clear folder history:', error);
            }
        }
    };

    const handleIndex = async () => {
        await handleSave();
        try {
            await axios.post('http://localhost:8000/api/index');
        } catch (error) {
            console.error('Failed to index:', error);
        }
    };

    const handleDeleteAllHistory = async () => {
        if (confirm('Delete all search history?')) {
            try {
                await axios.delete('http://localhost:8000/api/search/history');
                alert('History cleared!');
            } catch (error) {
                console.error('Failed to clear history:', error);
            }
        }
    };

    const handleClearCache = async () => {
        if (confirm('Clear all AI response cache? This will reset the learning.')) {
            try {
                await axios.post('http://localhost:8000/api/cache/clear');
                await fetchCacheStats();
                alert('Cache cleared!');
            } catch (error) {
                console.error('Failed to clear cache:', error);
            }
        }
    };

    const toggleSection = (section) => {
        setExpandedSection(expandedSection === section ? null : section);
    };

    const apiProviders = [
        { id: 'openai', name: 'OpenAI (ChatGPT)', key: 'openai_api_key', placeholder: 'sk-...' },
        { id: 'gemini', name: 'Google Gemini', key: 'gemini_api_key', placeholder: 'AIza...' },
        { id: 'anthropic', name: 'Anthropic (Claude)', key: 'anthropic_api_key', placeholder: 'sk-ant-...' },
        { id: 'grok', name: 'xAI (Grok)', key: 'grok_api_key', placeholder: 'xai-...' },
    ];

    const localModels = [
        { id: 'llamacpp', name: 'LlamaCpp (GGUF)', desc: 'Run .gguf model files directly' },
    ];

    if (!isOpen) return null;

    return (
        <div
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
            onClick={(e) => {
                if (e.target === e.currentTarget) onClose();
            }}
        >
            <div className="glass-overlay w-full max-w-xl max-h-[85vh] overflow-y-auto rounded-2xl shadow-2xl">
                {/* Header */}
                <div className="sticky top-0 z-10 flex items-center justify-between p-4 border-b border-border/30 bg-background/80 backdrop-blur-md">
                    <h2 className="text-lg font-bold flex items-center gap-3">
                        <div className="p-2 rounded-xl bg-primary/10">
                            <Settings className="w-5 h-5 text-primary" />
                        </div>
                        Settings
                    </h2>
                    <button
                        onClick={onClose}
                        className="p-2 rounded-xl hover:bg-secondary transition-colors"
                        aria-label="Close settings"
                    >
                        <X className="w-4 h-4" />
                    </button>
                </div>

                <div className="p-4 space-y-4">
                    {/* Indexing Progress */}
                    {indexingStatus.running && (
                        <div className="p-4 rounded-xl glass-v2 border border-primary/20 bg-primary/5">
                            <div className="flex justify-between items-center mb-2">
                                <span className="text-sm font-bold text-primary flex items-center gap-2">
                                    <Loader2 className="w-4 h-4 animate-spin" />
                                    Indexing...
                                </span>
                                <span className="text-xs font-mono font-bold text-primary">
                                    {indexingStatus.progress}%
                                </span>
                            </div>
                            <div className="w-full bg-primary/10 rounded-full h-2 overflow-hidden">
                                <div
                                    className="bg-primary h-full transition-all duration-300"
                                    style={{ width: `${indexingStatus.progress}%` }}
                                />
                            </div>
                            <div className="text-[10px] text-muted-foreground truncate opacity-80 font-mono mt-1">
                                {indexingStatus.current_file}
                            </div>
                        </div>
                    )}

                    {/* Indexing Error */}
                    {indexingStatus.error && !indexingStatus.running && (
                        <div className="p-4 rounded-xl glass-v2 border border-destructive/20 bg-destructive/5 flex items-center gap-3">
                            <div className="p-2 rounded-full bg-destructive/10 text-destructive">
                                <X className="w-4 h-4" />
                            </div>
                            <div className="text-sm font-medium text-destructive">
                                {indexingStatus.error}
                            </div>
                        </div>
                    )}

                    {/* Folder Section */}
                    <section className="space-y-3">
                        <div className="flex justify-between items-center">
                            <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-widest">
                                Indexed Folders
                            </h3>
                            <button
                                onClick={handleAddFolder}
                                className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-primary/10 text-primary text-xs font-bold hover:bg-primary/20 transition-colors"
                            >
                                <FolderOpen className="w-3.5 h-3.5" />
                                Add Folder
                            </button>

                            {/* History Dropdown */}
                            {folderHistory.length > 0 && (
                                <div className="relative">
                                    <button
                                        onClick={() => setShowHistory(!showHistory)}
                                        className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-secondary/20 text-secondary-foreground text-xs font-bold hover:bg-secondary/30 transition-colors ml-2"
                                        title="Previously indexed folders"
                                    >
                                        <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                                        Recently Indexed
                                        {showHistory ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                                    </button>

                                    {showHistory && (
                                        <div className="absolute right-0 top-full mt-2 w-72 bg-card border border-border rounded-xl shadow-xl z-50 overflow-hidden">
                                            <div className="p-2 border-b border-border bg-muted/30 flex justify-between items-center">
                                                <h4 className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Recently Indexed</h4>
                                                <button
                                                    onClick={handleClearAllHistory}
                                                    className="text-[10px] text-destructive hover:text-destructive/80 font-medium"
                                                    title="Clear all folder history"
                                                >
                                                    Clear All
                                                </button>
                                            </div>
                                            <div className="max-h-48 overflow-y-auto py-1">
                                                {folderHistory.length > 0 ? (
                                                    folderHistory.map((folder, idx) => {
                                                        const isAdded = config.folders.includes(folder);
                                                        return (
                                                            <div
                                                                key={idx}
                                                                className={`flex items-center gap-1 px-2 py-1.5 group ${isAdded ? 'opacity-50' : 'hover:bg-accent'}`}
                                                            >
                                                                <button
                                                                    onClick={() => !isAdded && handleAddFromHistory(folder)}
                                                                    disabled={isAdded}
                                                                    className="flex-1 text-left text-xs truncate flex items-center gap-2"
                                                                    title={isAdded ? "Already added" : `Add: ${folder}`}
                                                                >
                                                                    <FolderOpen className="w-3 h-3 opacity-50 flex-shrink-0" />
                                                                    <span className="truncate">{folder}</span>
                                                                    {isAdded && <span className="text-[10px] bg-green-500/10 text-green-600 px-1 rounded ml-auto">Added</span>}
                                                                </button>
                                                                <button
                                                                    onClick={(e) => handleRemoveFromHistory(folder, e)}
                                                                    className="p-1 rounded hover:bg-destructive/20 hover:text-destructive opacity-0 group-hover:opacity-100 transition-opacity"
                                                                    title="Remove from history"
                                                                    aria-label={`Remove ${folder} from history`}
                                                                >
                                                                    <Trash2 className="w-3 h-3" />
                                                                </button>
                                                            </div>
                                                        );
                                                    })
                                                ) : (
                                                    <div className="px-3 py-4 text-center text-xs text-muted-foreground italic">
                                                        No indexed folders found
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>

                        <div className="space-y-2">
                            {config.folders.length > 0 ? (
                                config.folders.map((folder, idx) => (
                                    <div key={idx} className="flex items-center gap-2 group p-2 rounded-lg border border-border bg-card/50">
                                        <div className="flex-1 min-w-0 flex items-center gap-2">
                                            <div className="p-1 rounded-full bg-green-500/10 text-green-500">
                                                <CheckCircle2 className="w-3 h-3" />
                                            </div>
                                            <p className="text-xs font-medium truncate opacity-80">{folder}</p>
                                        </div>
                                        <button
                                            onClick={() => handleRemoveFolder(folder)}
                                            className="p-1.5 rounded-md hover:bg-destructive/10 hover:text-destructive opacity-0 group-hover:opacity-100 transition-all"
                                            aria-label={`Remove ${folder} from index`}
                                        >
                                            <Trash2 className="w-3.5 h-3.5" />
                                        </button>
                                    </div>
                                ))
                            ) : (
                                <div className="text-center py-6 border-2 border-dashed border-border rounded-xl">
                                    <p className="text-sm text-muted-foreground">No folders selected</p>
                                </div>
                            )}
                        </div>

                        <button
                            onClick={handleIndex}
                            disabled={config.folders.length === 0 || indexingStatus.running}
                            className="w-full py-2.5 rounded-xl bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50 text-sm font-bold shadow-lg shadow-primary/20 transition-all active:scale-[0.98] mt-2"
                        >
                            {indexingStatus.running ? 'Indexing...' : 'Rebuild Index'}
                        </button>

                        {/* Indexing Progress Bar */}
                        {indexingStatus.running && (
                            <div className="mt-3 space-y-1.5 animate-in fade-in duration-300">
                                <div className="flex justify-between text-xs font-medium text-muted-foreground">
                                    <span>Processing: {indexingStatus.current_file ? indexingStatus.current_file.split('/').pop() : 'Initializing...'}</span>
                                    <span>{indexingStatus.progress}%</span>
                                </div>
                                <div className="h-2 w-full bg-secondary rounded-full overflow-hidden">
                                    <div
                                        className="h-full bg-primary transition-all duration-300 ease-out"
                                        style={{ width: `${indexingStatus.progress}%` }}
                                    />
                                </div>
                            </div>
                        )}
                    </section>

                    {/* AI Provider Selection */}
                    <section className="space-y-3">
                        <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
                            AI Provider
                        </h3>
                        <select
                            value={config.provider}
                            onChange={(e) => setConfig({ ...config, provider: e.target.value })}
                            className="w-full px-3 py-2 text-sm rounded-lg border border-input bg-background"
                        >
                            <option value="local">Local Models (Free)</option>
                            <option value="openai">OpenAI (ChatGPT)</option>
                            <option value="gemini">Google Gemini</option>
                            <option value="anthropic">Anthropic (Claude)</option>
                            <option value="grok">xAI (Grok)</option>
                        </select>
                    </section>

                    {/* Local Model Options */}
                    {config.provider === 'local' && (
                        <section className="space-y-3">
                            <button
                                onClick={() => toggleSection('local')}
                                className="w-full flex items-center justify-between text-sm font-medium text-muted-foreground uppercase tracking-wide"
                            >
                                <span className="flex items-center gap-2">
                                    <Cpu className="w-4 h-4" />
                                    Local Model Settings
                                </span>
                                {expandedSection === 'local' ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                            </button>

                            {expandedSection === 'local' && (
                                <div className="space-y-3 pl-2 border-l-2 border-border ml-2">
                                    {/* Active Model Banner */}
                                    {activeModel && (
                                        <div className="p-4 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-between mb-4">
                                            <div>
                                                <div className="text-[10px] uppercase font-bold text-primary tracking-wider mb-0.5">Currently Active</div>
                                                <div className="text-sm font-bold flex items-center gap-2">
                                                    <Cpu className="w-4 h-4 text-primary" />
                                                    {activeModel}
                                                </div>
                                            </div>
                                            <div className="px-2 py-0.5 bg-primary text-primary-foreground text-[10px] rounded-md font-bold uppercase tracking-widest">
                                                Active
                                            </div>
                                        </div>
                                    )}

                                    {localModels.length > 1 && (
                                        <div className="space-y-2">
                                            <label className="text-sm">Model Type</label>
                                            <div className="space-y-2">
                                                {localModels.map(model => (
                                                    <label key={model.id} className="flex items-start gap-3 p-3 rounded-lg border border-border hover:bg-accent cursor-pointer">
                                                        <input
                                                            type="radio"
                                                            name="localModelType"
                                                            value={model.id}
                                                            checked={config.local_model_type === model.id}
                                                            onChange={(e) => setConfig({ ...config, local_model_type: e.target.value })}
                                                            className="mt-0.5"
                                                        />
                                                        <div>
                                                            <div className="font-medium text-sm">{model.name}</div>
                                                            <div className="text-xs text-muted-foreground">{model.desc}</div>
                                                        </div>
                                                    </label>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    <ModelManager
                                        onSelectModel={(path) => setConfig({ ...config, local_model_path: path })}
                                        activeModel={activeModel}
                                        selectedPath={config.local_model_path}
                                    />
                                </div>
                            )}
                        </section>
                    )}

                    {/* API Keys Section */}
                    <section className="space-y-3">
                        <button
                            onClick={() => toggleSection('apikeys')}
                            className="w-full flex items-center justify-between text-sm font-medium text-muted-foreground uppercase tracking-wide"
                        >
                            <span className="flex items-center gap-2">
                                <Key className="w-4 h-4" />
                                API Keys
                            </span>
                            {expandedSection === 'apikeys' ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                        </button>

                        {expandedSection === 'apikeys' && (
                            <div className="space-y-3 pl-2 border-l-2 border-border ml-2">
                                {apiProviders.map(provider => (
                                    <div key={provider.id} className="space-y-1">
                                        <label className="text-sm font-medium">{provider.name}</label>
                                        <input
                                            type="password"
                                            value={config[provider.key] || ''}
                                            onChange={(e) => setConfig({ ...config, [provider.key]: e.target.value })}
                                            className="w-full px-3 py-2 text-sm rounded-lg border border-input bg-background"
                                            placeholder={provider.placeholder}
                                        />
                                    </div>
                                ))}
                                <p className="text-xs text-muted-foreground">
                                    API keys are stored locally and used only when that provider is selected.
                                </p>
                            </div>
                        )}
                    </section>

                    {/* Data Management */}
                    <section className="space-y-3 pt-3 border-t border-border">
                        <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
                            Data Management
                        </h3>

                        {/* Cache Stats */}
                        <div className="flex items-center justify-between p-3 rounded-lg border border-border bg-card/50">
                            <div>
                                <div className="text-sm font-semibold flex items-center gap-2">
                                    <span className="text-primary">⚡</span> AI Response Cache
                                </div>
                                <div className="text-xs text-muted-foreground">
                                    {cacheStats.total_entries} entries • {cacheStats.total_hits} hits saved
                                </div>
                            </div>
                            <button
                                onClick={handleClearCache}
                                className="px-3 py-1.5 text-xs font-medium rounded-lg bg-destructive/10 text-destructive hover:bg-destructive/20 transition-colors"
                            >
                                Clear Cache
                            </button>
                        </div>

                        <button
                            onClick={handleDeleteAllHistory}
                            className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-destructive hover:bg-destructive/10 transition-colors"
                        >
                            <Trash2 className="w-4 h-4" />
                            Clear Search History
                        </button>
                    </section>
                </div>

                {/* Footer */}
                <div className="sticky bottom-0 p-4 border-t border-border/30 bg-background/80 backdrop-blur-md flex justify-end gap-3">
                    <button
                        onClick={onClose}
                        className="px-4 py-2.5 rounded-xl text-sm font-medium hover:bg-secondary transition-colors"
                    >
                        Cancel
                    </button>
                    <button
                        onClick={handleSave}
                        disabled={isLoading}
                        className="px-5 py-2.5 rounded-xl btn-cosmic text-sm font-semibold flex items-center gap-2 disabled:opacity-50"
                    >
                        {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                        Save Changes
                    </button>
                </div>
            </div>
        </div>
    );
};

export default SettingsModal;
