import React, { useState, useRef, useEffect } from 'react';
import { Search, Loader2, Bot, Zap } from 'lucide-react';
import { motion } from 'framer-motion';

const SearchBar = ({ onSearch, isLoading, isAgentMode, onToggleAgent }) => {
    const [query, setQuery] = useState('');
    const [isFocused, setIsFocused] = useState(false);
    const [shortcutHint, setShortcutHint] = useState('Ctrl + K');
    const inputRef = useRef(null);

    useEffect(() => {
        // Detect platform for correct shortcut hint
        const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
        setShortcutHint(isMac ? '⌘K' : 'Ctrl + K');

        const handleKeyDown = (e) => {
            // Cmd+K or Ctrl+K
            if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
                e.preventDefault();
                inputRef.current?.focus();
            }
            // Slash key (/)
            if (e.key === '/' && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') {
                e.preventDefault();
                inputRef.current?.focus();
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, []);

    const handleSubmit = (e) => {
        e.preventDefault();
        if (query.trim()) {
            onSearch(query);
        }
    };

    return (
        <div className="w-full">
            <form onSubmit={handleSubmit}>
                <motion.div
                    className={`relative flex items-center rounded-2xl transition-all duration-300 ${isFocused
                            ? 'glass-card shadow-lg shadow-primary/10'
                            : 'glass-card'
                        }`}
                    animate={isFocused ? { scale: 1.01 } : { scale: 1 }}
                    transition={{ duration: 0.2 }}
                >
                    {/* Search Icon with Glow */}
                    <div className={`absolute left-5 transition-all duration-300 ${isFocused ? 'text-primary' : 'text-muted-foreground'}`}>
                        <Search className="w-5 h-5" />
                    </div>

                    {/* Input Field */}
                    <input
                        ref={inputRef}
                        type="text"
                        aria-label="Search query"
                        className="w-full bg-transparent py-4 pl-14 pr-32 text-base placeholder:text-muted-foreground/70 focus:outline-none"
                        placeholder={isAgentMode ? "Ask the AI Researcher a complex question..." : "Search your documents..."}
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        onFocus={() => setIsFocused(true)}
                        onBlur={() => setIsFocused(false)}
                        disabled={isLoading}
                    />

                    {/* Keyboard Shortcut Hint */}
                    {!isFocused && !query && (
                        <div className="absolute right-28 pointer-events-none hidden md:flex items-center gap-1">
                            <span className="text-xs font-medium text-muted-foreground/50 border border-border/50 rounded px-1.5 py-0.5 bg-background/50 backdrop-blur-sm">
                                {shortcutHint}
                            </span>
                        </div>
                    )}

                    {/* Right Side Actions */}
                    <div className="absolute right-3 flex items-center gap-2">
                        {/* Agent Mode Toggle */}
                        {onToggleAgent && (
                            <button
                                type="button"
                                onClick={onToggleAgent}
                                aria-label="Toggle AI Agent Mode"
                                className={`p-2 rounded-xl transition-all duration-200 ${isAgentMode
                                        ? 'bg-accent/20 text-accent border border-accent/30'
                                        : 'hover:bg-secondary text-muted-foreground'
                                    }`}
                                title={isAgentMode ? "Agent Mode Active" : "Enable Agent Mode"}
                            >
                                <Bot className="w-4 h-4" />
                            </button>
                        )}

                        {/* Search Button */}
                        <button
                            type="submit"
                            aria-label="Submit Search"
                            disabled={isLoading || !query.trim()}
                            className="p-2.5 rounded-xl btn-cosmic disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                        >
                            {isLoading ? (
                                <Loader2 className="w-4 h-4 animate-spin" />
                            ) : (
                                <Zap className="w-4 h-4" />
                            )}
                        </button>
                    </div>
                </motion.div>
            </form>

            {/* Agent Mode Indicator */}
            {isAgentMode && (
                <motion.div
                    initial={{ opacity: 0, y: -5 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-3 flex items-center justify-center gap-2 text-xs text-accent"
                >
                    <Bot className="w-3.5 h-3.5" />
                    <span>AI Researcher Mode - Complex reasoning enabled</span>
                </motion.div>
            )}
        </div>
    );
};

export default SearchBar;