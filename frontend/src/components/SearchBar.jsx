import React, { useState } from 'react';
import { Search, Loader2 } from 'lucide-react';

const SearchBar = ({ onSearch, isLoading, isAgentMode, onToggleAgent }) => {
    const [query, setQuery] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (query.trim()) {
            onSearch(query);
        }
    };

    return (
        <div className="w-full">
            <form onSubmit={handleSubmit}>
                <div className="relative flex items-center">
                    <Search className="absolute left-4 w-5 h-5 text-muted-foreground" />
                    <input
                        type="text"
                        className="w-full bg-secondary border border-border rounded-lg py-3 pl-12 pr-4 text-base placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-background"
                        placeholder={isAgentMode ? "Ask the AI Researcher a complex question..." : "What are you looking for?"}
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        disabled={isLoading}
                    />
                    {isLoading && <Loader2 className="absolute right-4 w-5 h-5 animate-spin text-muted-foreground" />}
                </div>
            </form>
        </div>
    );
};

export default SearchBar;