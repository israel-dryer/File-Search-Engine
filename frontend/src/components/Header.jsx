import React, { useState } from 'react';
import { Settings, Moon, Sun, Cpu, ChevronDown, Check, History, Sparkles } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const Header = ({ darkMode, toggleDarkMode, openSettings, toggleHistory, isHistoryOpen, activeModel, availableModels = [], onModelChange, indexingStatus }) => {
    const [isModelDropdownOpen, setIsModelDropdownOpen] = useState(false);

    const handleModelSelect = (modelName) => {
        onModelChange(modelName);
        setIsModelDropdownOpen(false);
    };

    return (
        <header className="sticky top-0 z-40 w-full glass-nav">
            <div className="container flex h-16 items-center px-4 max-w-7xl mx-auto">
                {/* Left: History + Logo */}
                <div className="flex items-center gap-3">
                    <button
                        onClick={toggleHistory}
                        className={`p-2.5 rounded-xl transition-all duration-200 hover:bg-primary/10 hover:text-primary ${isHistoryOpen ? 'bg-primary/15 text-primary' : 'text-muted-foreground'}`}
                        aria-label="Toggle history"
                    >
                        <History className="w-5 h-5" />
                    </button>
                    <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-accent flex items-center justify-center">
                            <Sparkles className="w-4 h-4 text-white" />
                        </div>
                        <h1 className="text-lg font-bold tracking-tight bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text">
                            File Search
                        </h1>
                    </div>
                </div>

                {/* Center: Model Selector */}
                <div className="flex-1 flex items-center justify-center">
                    {activeModel && (
                        <div className="relative">
                            <button
                                onClick={() => setIsModelDropdownOpen(!isModelDropdownOpen)}
                                className="flex items-center gap-2.5 px-4 py-2 rounded-xl glass-card hover:border-primary/30 transition-all text-sm font-medium group"
                            >
                                <div className="p-1.5 rounded-md bg-primary/10">
                                    <Cpu className="w-3.5 h-3.5 text-primary" />
                                </div>
                                <span className="truncate max-w-[120px] sm:max-w-[200px]">{activeModel}</span>
                                <ChevronDown className={`w-4 h-4 text-muted-foreground transition-transform duration-300 ${isModelDropdownOpen ? 'rotate-180' : ''}`} />
                            </button>

                            <AnimatePresence>
                                {isModelDropdownOpen && (
                                    <motion.div
                                        initial={{ opacity: 0, y: -8, scale: 0.95 }}
                                        animate={{ opacity: 1, y: 8, scale: 1 }}
                                        exit={{ opacity: 0, y: -8, scale: 0.95 }}
                                        transition={{ duration: 0.2 }}
                                        className="absolute top-full left-1/2 -translate-x-1/2 mt-2 w-72 p-2 rounded-xl glass-overlay shadow-xl"
                                    >
                                        <div className="text-xs font-bold text-muted-foreground uppercase tracking-wider px-3 py-2">
                                            Available Models
                                        </div>
                                        <div className="max-h-64 overflow-y-auto space-y-1">
                                            {availableModels.length > 0 ? (
                                                availableModels.map((model, index) => {
                                                    const modelName = model.name.replace('.gguf', '');
                                                    const isActive = activeModel === modelName;
                                                    return (
                                                        <button
                                                            key={index}
                                                            onClick={() => handleModelSelect(modelName)}
                                                            className={`w-full text-left px-3 py-2.5 rounded-lg text-sm transition-all flex items-center justify-between group
                                                                ${isActive
                                                                    ? 'bg-primary/15 text-primary font-semibold border border-primary/20'
                                                                    : 'hover:bg-secondary/80'}`}
                                                        >
                                                            <span className="truncate">{modelName}</span>
                                                            {isActive && (
                                                                <div className="p-1 rounded-full bg-primary/20">
                                                                    <Check className="w-3 h-3 text-primary" />
                                                                </div>
                                                            )}
                                                        </button>
                                                    );
                                                })
                                            ) : (
                                                <div className="px-3 py-4 text-sm text-muted-foreground text-center">
                                                    No local models found
                                                    <p className="text-xs mt-1">Go to Settings → Model Manager</p>
                                                </div>
                                            )}
                                        </div>
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </div>
                    )}

                    {/* Indexing Indicator */}
                    {indexingStatus?.running && (
                        <div className="ml-4 flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/20">
                            <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />
                            <span className="text-xs font-medium text-primary">{indexingStatus.progress}%</span>
                        </div>
                    )}
                </div>

                {/* Right: Theme + Settings */}
                <div className="flex items-center gap-2">
                    <button
                        onClick={toggleDarkMode}
                        className="p-2.5 rounded-xl transition-all duration-200 hover:bg-secondary text-muted-foreground hover:text-foreground"
                        aria-label="Toggle theme"
                    >
                        {darkMode ? (
                            <Sun className="w-5 h-5" />
                        ) : (
                            <Moon className="w-5 h-5" />
                        )}
                    </button>
                    <button
                        onClick={openSettings}
                        className="p-2.5 rounded-xl transition-all duration-200 hover:bg-secondary text-muted-foreground hover:text-foreground"
                        aria-label="Settings"
                    >
                        <Settings className="w-5 h-5" />
                    </button>
                </div>
            </div>
        </header>
    );
};

export default Header;
