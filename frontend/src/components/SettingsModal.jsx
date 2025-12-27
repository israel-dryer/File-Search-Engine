import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { X, Settings, FolderOpen, Loader2, Save, ChevronDown, ChevronUp, Key, Cpu, Trash2 } from 'lucide-react';
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

    const handleAddFolder = async () => {
        try {
            const response = await axios.get('http://localhost:8000/api/browse');
            if (response.data.folder && !config.folders.includes(response.data.folder)) {
                setConfig(prev => ({
                    ...prev,
                    folders: [...prev.folders, response.data.folder]
                }));
            }
        } catch (error) {
            console.error('Failed to browse:', error);
        }
    };

    const handleRemoveFolder = (folderToRemove) => {
        setConfig(prev => ({
            ...prev,
            folders: prev.folders.filter(f => f !== folderToRemove)
        }));
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
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
            <div className="bg-background w-full max-w-xl max-h-[85vh] overflow-y-auto rounded-xl border border-border shadow-2xl">
                {/* Header */}
                <div className="sticky top-0 z-10 flex items-center justify-between p-4 border-b border-border bg-background">
                    <h2 className="text-lg font-semibold flex items-center gap-2">
                        <Settings className="w-5 h-5" />
                        Settings
                    </h2>
                    <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-accent">
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
                            <div className="text-[10px] text-muted-foreground truncate opacity-80">
                                {indexingStatus.current_file}
                            </div>
                        </div>
                    )}

                    {/* Folder Section */}
                    <section className="space-y-3">
                        <div className="flex justify-between items-center">
                            <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-widest">
                                Document Folders
                            </h3>
                            <button
                                onClick={handleAddFolder}
                                className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-primary/10 text-primary text-xs font-bold hover:bg-primary/20 transition-colors"
                            >
                                <FolderOpen className="w-3.5 h-3.5" />
                                Add Folder
                            </button>
                        </div>

                        <div className="space-y-2">
                            {config.folders.length > 0 ? (
                                config.folders.map((folder, idx) => (
                                    <div key={idx} className="flex items-center gap-2 group p-2 rounded-lg border border-border bg-card/50">
                                        <div className="flex-1 min-w-0">
                                            <p className="text-xs font-medium truncate opacity-80">{folder}</p>
                                        </div>
                                        <button
                                            onClick={() => handleRemoveFolder(folder)}
                                            className="p-1.5 rounded-md hover:bg-destructive/10 hover:text-destructive opacity-0 group-hover:opacity-100 transition-all"
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
                <div className="sticky bottom-0 p-4 border-t border-border bg-background flex justify-end gap-2">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 rounded-lg text-sm hover:bg-accent transition-colors"
                    >
                        Cancel
                    </button>
                    <button
                        onClick={handleSave}
                        disabled={isLoading}
                        className="px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 flex items-center gap-2"
                    >
                        {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                        Save
                    </button>
                </div>
            </div>
        </div>
    );
};

export default SettingsModal;
