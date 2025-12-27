import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Download, Trash2, Check, Loader2, HardDrive, AlertCircle, Star, Cpu, Search, Filter } from 'lucide-react';

const ModelManager = ({ onSelectModel, activeModel, selectedPath }) => {
    const [availableModels, setAvailableModels] = useState([]);
    const [localModels, setLocalModels] = useState([]);
    const [downloadStatus, setDownloadStatus] = useState({ downloading: false });
    const [error, setError] = useState(null);
    const [filter, setFilter] = useState('all');
    const [searchQuery, setSearchQuery] = useState('');

    useEffect(() => {
        fetchModels();
        const interval = setInterval(checkDownloadStatus, 2000);
        return () => clearInterval(interval);
    }, []);

    const fetchModels = async () => {
        try {
            const [available, local] = await Promise.all([
                axios.get('http://localhost:8000/api/models/available'),
                axios.get('http://localhost:8000/api/models/local')
            ]);
            setAvailableModels(available.data || []);
            setLocalModels(local.data || []);
        } catch (err) {
            console.error('Failed to fetch models:', err);
        }
    };

    const checkDownloadStatus = async () => {
        try {
            const response = await axios.get('http://localhost:8000/api/models/status');
            setDownloadStatus(response.data);

            if (!response.data.downloading && downloadStatus.downloading) {
                fetchModels();
            }
        } catch (err) {
            // Ignore
        }
    };

    const handleDownload = async (modelId) => {
        setError(null);
        try {
            const response = await axios.post(`http://localhost:8000/api/models/download/${modelId}`);
            if (response.data.status === 'success') {
                setDownloadStatus({ downloading: true, model_id: modelId, progress: 0 });
            }
            // Show warning if present
            if (response.data.message?.includes('Warnings')) {
                setError(response.data.message);
            }
        } catch (err) {
            setError(err.response?.data?.detail || 'Download failed');
        }
    };

    const handleDelete = async (modelPath) => {
        if (!confirm('Delete this model?')) return;
        try {
            await axios.delete('http://localhost:8000/api/models/delete', {
                data: { path: modelPath }
            });
            fetchModels();
        } catch (err) {
            setError('Failed to delete');
        }
    };

    const isDownloaded = (modelId) => {
        return localModels.some(m => m.id === modelId || m.filename?.includes(modelId));
    };

    const formatSize = (bytes) => {
        if (!bytes) return '';
        const gb = bytes / (1024 * 1024 * 1024);
        return gb >= 1 ? `${gb.toFixed(1)} GB` : `${(bytes / (1024 * 1024)).toFixed(0)} MB`;
    };

    const normalize = (name) => name?.toLowerCase().replace('.gguf', '') || '';

    const getCategoryColor = (category) => {
        switch (category) {
            case 'small': return 'text-green-500 bg-green-500/10';
            case 'medium': return 'text-yellow-500 bg-yellow-500/10';
            case 'large': return 'text-red-500 bg-red-500/10';
            default: return 'text-muted-foreground bg-muted';
        }
    };

    const getCategoryLabel = (category) => {
        switch (category) {
            case 'small': return 'Fast';
            case 'medium': return 'Balanced';
            case 'large': return 'Quality';
            default: return category;
        }
    };

    const normalizePath = (path) => {
        if (!path) return '';
        return path.replace(/\\/g, '/').toLowerCase();
    };

    const filteredModels = availableModels.filter(model => {
        const matchesFilter = filter === 'all' || model.category === filter;
        const matchesSearch = !searchQuery ||
            model.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
            model.description.toLowerCase().includes(searchQuery.toLowerCase());
        return matchesFilter && matchesSearch;
    });

    const categories = ['all', 'small', 'medium', 'large'];

    return (
        <div className="space-y-4">
            {error && (
                <div className="flex items-center gap-2 p-2 rounded-lg bg-destructive/10 text-destructive text-sm">
                    <AlertCircle className="w-4 h-4 shrink-0" />
                    <span className="flex-1">{error}</span>
                    <button onClick={() => setError(null)} className="text-xs underline">Dismiss</button>
                </div>
            )}

            {/* Downloaded Models */}
            <div>
                <h4 className="text-sm font-medium mb-2 flex items-center gap-2">
                    <HardDrive className="w-4 h-4" />
                    Downloaded ({localModels.length})
                </h4>
                {localModels.length > 0 ? (
                    <div className="space-y-2">
                        {localModels.map((model, idx) => {
                            // Use selectedPath if available, otherwise fallback to name matching for activeModel (for backward compatibility or initial load)
                            // But for the specific "Select" button state, we prioritize the selectedPath prop.
                            const isSelected = selectedPath ? normalizePath(model.path) === normalizePath(selectedPath) : normalize(model.name) === normalize(activeModel);
                            // Active means it is the one possibly currently running in the backend (activeModel)
                            const isActiveRunning = normalize(model.name) === normalize(activeModel);

                            return (
                                <div
                                    key={idx}
                                    className={`flex items-center justify-between p-2 rounded-lg border transition-all duration-200 ${isSelected
                                        ? 'border-primary bg-primary/5 shadow-sm ring-1 ring-primary/20'
                                        : 'border-border bg-card'
                                        }`}
                                >
                                    <div className="flex items-center gap-2 min-w-0 flex-1">
                                        <HardDrive className={`w-4 h-4 shrink-0 ${isSelected ? 'text-primary' : 'text-green-500'}`} />
                                        <div className="min-w-0">
                                            <div className="flex items-center gap-2">
                                                <p className={`text-sm font-medium truncate ${isSelected ? 'text-primary' : ''}`}>
                                                    {model.name}
                                                </p>
                                                {isActiveRunning && (
                                                    <span className="px-1.5 py-0.5 text-[10px] font-bold uppercase rounded bg-primary text-primary-foreground">
                                                        Active
                                                    </span>
                                                )}
                                            </div>
                                            <div className="flex items-center gap-2 text-xs text-muted-foreground">
                                                <span>{formatSize(model.size)}</span>
                                                {model.ram_required && (
                                                    <span className="flex items-center gap-1">
                                                        <Cpu className="w-3 h-3" />
                                                        {model.ram_required}GB RAM
                                                    </span>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-1">
                                        <button
                                            onClick={() => onSelectModel && onSelectModel(model.path)}
                                            className={`px-2 py-1 text-xs font-medium rounded shrink-0 transition-colors ${isSelected
                                                ? 'bg-primary text-primary-foreground pointer-events-none opacity-50'
                                                : 'bg-primary/10 text-primary hover:bg-primary/20'
                                                }`}
                                        >
                                            {isSelected ? 'Selected' : 'Select'}
                                        </button>
                                        <button
                                            onClick={() => handleDelete(model.path)}
                                            className="p-1.5 rounded hover:bg-destructive/10 hover:text-destructive shrink-0"
                                            title="Delete Model"
                                        >
                                            <Trash2 className="w-4 h-4" />
                                        </button>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                ) : (
                    <p className="text-sm text-muted-foreground p-4 text-center">No models downloaded</p>
                )}
            </div>

            {/* Available Models */}
            <div>
                <h4 className="text-sm font-medium mb-2">Available Models</h4>

                {/* Filters */}
                <div className="flex gap-2 mb-3">
                    <div className="relative flex-1">
                        <Search className="absolute left-2 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                        <input
                            type="text"
                            placeholder="Search models..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="w-full pl-8 pr-2 py-1.5 text-sm rounded-lg border border-border bg-background"
                        />
                    </div>
                </div>

                {/* Category Tabs */}
                <div className="flex gap-1 mb-3">
                    {categories.map(cat => (
                        <button
                            key={cat}
                            onClick={() => setFilter(cat)}
                            className={`px-2 py-1 text-xs rounded-md transition-colors ${filter === cat
                                ? 'bg-primary text-primary-foreground'
                                : 'bg-muted hover:bg-muted/80'
                                }`}
                        >
                            {cat === 'all' ? 'All' : getCategoryLabel(cat)}
                        </button>
                    ))}
                </div>

                <div className="space-y-2 max-h-[300px] overflow-y-auto custom-scrollbar">
                    {filteredModels.map((model) => (
                        <div
                            key={model.id}
                            className={`p-2 rounded-lg border ${model.recommended ? 'border-primary/50 bg-primary/5' : 'border-border'
                                }`}
                        >
                            <div className="flex items-start justify-between gap-2">
                                <div className="min-w-0 flex-1">
                                    <div className="flex items-center gap-2">
                                        <p className="text-sm font-medium">{model.name}</p>
                                        {model.recommended && (
                                            <Star className="w-3 h-3 text-yellow-500 fill-yellow-500" />
                                        )}
                                    </div>
                                    <p className="text-xs text-muted-foreground mt-0.5">{model.description}</p>
                                    <div className="flex items-center gap-2 mt-1 flex-wrap">
                                        <span className={`px-1.5 py-0.5 text-xs rounded ${getCategoryColor(model.category)}`}>
                                            {getCategoryLabel(model.category)}
                                        </span>
                                        <span className="text-xs text-muted-foreground">{model.size}</span>
                                        <span className="text-xs text-muted-foreground flex items-center gap-1">
                                            <Cpu className="w-3 h-3" />
                                            {model.ram_required}GB
                                        </span>
                                        <span className="text-xs text-muted-foreground">{model.quantization}</span>
                                    </div>
                                </div>
                                <div className="shrink-0">
                                    {isDownloaded(model.id) ? (
                                        <div className="flex items-center gap-1 text-green-500">
                                            <Check className="w-4 h-4" />
                                            <span className="text-xs">Ready</span>
                                        </div>
                                    ) : downloadStatus.downloading && downloadStatus.model_id === model.id ? (
                                        <div className="flex flex-col items-end gap-1">
                                            <div className="flex items-center gap-1">
                                                <span className="text-xs">{downloadStatus.progress || 0}%</span>
                                                <Loader2 className="w-4 h-4 animate-spin" />
                                            </div>
                                            <div className="w-16 bg-muted rounded-full h-1">
                                                <div
                                                    className="bg-primary h-1 rounded-full transition-all"
                                                    style={{ width: `${downloadStatus.progress || 0}%` }}
                                                />
                                            </div>
                                        </div>
                                    ) : (
                                        <button
                                            onClick={() => handleDownload(model.id)}
                                            disabled={downloadStatus.downloading}
                                            className="flex items-center gap-1 px-2 py-1 text-xs rounded hover:bg-accent disabled:opacity-50"
                                        >
                                            <Download className="w-4 h-4" />
                                            Download
                                        </button>
                                    )}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>

                {filteredModels.length === 0 && (
                    <p className="text-sm text-muted-foreground text-center py-4">
                        No models match your search
                    </p>
                )}
            </div>
        </div>
    );
};

export default ModelManager;
