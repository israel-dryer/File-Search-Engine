import React, { useState, useEffect } from 'react';
import { History, Trash2, Clock, Search, X } from 'lucide-react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';

const SearchHistory = ({ onSelectQuery, isOpen, onClose, isMobile }) => {
    const [history, setHistory] = useState([]);
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        if (isOpen) {
            fetchHistory();
        }
    }, [isOpen]);

    const fetchHistory = async () => {
        setIsLoading(true);
        try {
            const response = await axios.get('http://localhost:8000/api/search/history');
            setHistory(response.data || []);
        } catch (error) {
            console.error('Failed to fetch history:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const deleteHistoryItem = async (id, e) => {
        e.stopPropagation();
        try {
            await axios.delete(`http://localhost:8000/api/search/history/${id}`);
            setHistory(history.filter(item => item.id !== id));
        } catch (error) {
            console.error('Failed to delete:', error);
        }
    };

    const formatTime = (timestamp) => {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        if (diff < 60000) return 'now';
        if (diff < 3600000) return `${Math.floor(diff / 60000)}m`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)}h`;
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    };

    if (!isOpen) return null;

    return (
        <AnimatePresence>
            <motion.div
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -10 }}
                className={`fixed left-0 top-16 bottom-0 bg-card/95 backdrop-blur-md border-r border-border z-30 shadow-2xl transition-all duration-300 ${isMobile ? 'w-full' : 'w-72'}`}
            >
                <div className="flex items-center justify-between px-4 py-4 border-b border-border/50 bg-secondary/20">
                    <div className="flex items-center gap-2">
                        <History className="w-4 h-4 text-primary" />
                        <span className="text-sm font-bold uppercase tracking-wider">Search History</span>
                    </div>
                    <button onClick={onClose} className="p-1 rounded hover:bg-accent">
                        <X className="w-4 h-4" />
                    </button>
                </div>

                <div className="overflow-y-auto h-[calc(100%-3rem)]">
                    {isLoading ? (
                        <div className="flex items-center justify-center py-8">
                            <div className="w-5 h-5 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                        </div>
                    ) : history.length === 0 ? (
                        <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
                            <Search className="w-8 h-8 mb-2 opacity-40" />
                            <p className="text-sm">No history</p>
                        </div>
                    ) : (
                        <div className="p-2">
                            {history.map((item) => (
                                <div
                                    key={item.id}
                                    className="group flex items-center justify-between px-3 py-2 rounded-lg hover:bg-accent cursor-pointer"
                                    onClick={() => { onSelectQuery(item.query); onClose(); }}
                                >
                                    <div className="flex-1 min-w-0 mr-2">
                                        <p className="text-sm truncate">{item.query}</p>
                                        <p className="text-xs text-muted-foreground">
                                            {formatTime(item.timestamp)} • {item.result_count} results
                                        </p>
                                    </div>
                                    <button
                                        onClick={(e) => deleteHistoryItem(item.id, e)}
                                        className="p-1 rounded opacity-0 group-hover:opacity-100 hover:bg-destructive/10 hover:text-destructive"
                                    >
                                        <Trash2 className="w-3.5 h-3.5" />
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </motion.div>
        </AnimatePresence>
    );
};

export default SearchHistory;
