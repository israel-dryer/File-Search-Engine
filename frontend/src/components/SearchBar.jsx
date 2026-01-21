import React, { useState } from 'react';
import { Search, Loader2, Bot, Brain } from 'lucide-react';

const SearchBar = ({ onSearch, isLoading, isAgentMode, onToggleAgent }) => {
    const [query, setQuery] = useState('');
    const [isFocused, setIsFocused] = useState(false);

    const handleSubmit = (e) => {
        e.preventDefault();
        if (query.trim()) {
            onSearch(query);
        }
    };

    return (
        <div className="w-full max-w-2xl mx-auto px-4 perspective-[1000px]">
            <form onSubmit={handleSubmit} className="transform-gpu transition-all duration-300">
                <div
                    className={`relative flex items-center glass-v2 rounded-2xl border transition-all duration-300 shadow-2xl ${isFocused
                        ? 'border-primary ring-4 ring-primary/10 -translate-y-2 scale-[1.02] shadow-primary/20'
                        : 'border-border'
                        }`}
                >
                    <div className="pl-5 flex items-center text-primary/60">
                        <Loader2 className="w-6 h-6 animate-spin" />
                        ) : (
                        <button
                            type="button"
                            onClick={onToggleAgent}
                            className={`transition-all duration-300 hover:scale-110 ${isAgentMode ? 'text-blue-500' : 'text-primary/60'}`}
                            title={isAgentMode ? "Switch to Standard Search" : "Switch to AI Agent Mode"}
                        >
                            {isAgentMode ? <Brain className="w-7 h-7" /> : <Search className="w-6 h-6" />}
                        </button>
                        )}
                    </div>
                    <input
                        type="text"
                        className="w-full bg-transparent py-4 pl-3 pr-4 text-lg font-medium placeholder:text-muted-foreground focus:outline-none"
                        placeholder={isAgentMode ? "Ask the AI Researcher a complex question..." : "What are you looking for?"}
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        onFocus={() => setIsFocused(true)}
                        onBlur={() => setIsFocused(false)}
                        disabled={isLoading}
                    />
                    {query && (
                        <button
                            type="submit"
                            className="mr-2.5 px-6 py-2 rounded-xl bg-primary text-primary-foreground font-bold shadow-lg hover:shadow-primary/40 hover:-translate-y-0.5 active:translate-y-0 transition-all duration-200 uppercase tracking-tighter"
                        >
                            Search
                        </button>
                    )}
                </div>
            </form>
        </div>
    );
};

export default SearchBar;
