import React, { useState } from 'react';
import { Settings, Moon, Sun, Cpu, ChevronDown, Check, History } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const Header = ({ darkMode, toggleDarkMode, openSettings, toggleHistory, isHistoryOpen, activeModel, availableModels = [], onModelChange }) => {
    const [isModelDropdownOpen, setIsModelDropdownOpen] = useState(false);

    const handleModelSelect = (modelName) => {
        onModelChange(modelName);
        setIsModelDropdownOpen(false);
    };

    return (
        <header className="sticky top-0 z-40 w-full border-b border-border/50 bg-background/95 backdrop-blur-sm">
            <div className="container flex h-14 items-center px-4 max-w-7xl mx-auto">
                <div className="flex items-center mr-4">
                    <button
                        onClick={toggleHistory}
                        className={`p-2 rounded-md transition-colors hover:bg-muted ${isHistoryOpen ? 'bg-muted' : ''}`}
                        aria-label="Toggle history"
                    >
                        <History className="w-5 h-5" />
                    </button>
                    <h1 className="text-lg font-semibold ml-2 tracking-tight">File Search</h1>
                </div>

                <div className="flex-1 flex items-center justify-center">
                    {activeModel && (
                        <div className="relative">
                            <button
                                onClick={() => setIsModelDropdownOpen(!isModelDropdownOpen)}
                                className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-secondary/50 border border-border/50 hover:bg-secondary transition-colors text-sm font-medium"
                            >
                                <Cpu className="w-4 h-4 text-primary" />
                                <span className="truncate max-w-[150px] sm:max-w-xs">{activeModel}</span>
                                <ChevronDown className={`w-4 h-4 text-muted-foreground transition-transform duration-200 ${isModelDropdownOpen ? 'rotate-180' : ''}`} />
                            </button>

                            <AnimatePresence>
                                {isModelDropdownOpen && (
                                    <motion.div
                                        initial={{ opacity: 0, y: -5 }}
                                        animate={{ opacity: 1, y: 5 }}
                                        exit={{ opacity: 0, y: -5 }}
                                        className="absolute top-full left-1/2 -translate-x-1/2 mt-2 w-64 p-1.5 rounded-lg bg-popover border border-border shadow-lg"
                                    >
                                        <div className="max-h-60 overflow-y-auto custom-scrollbar">
                                            {availableModels.length > 0 ? (
                                                availableModels.map((model, index) => {
                                                    const modelName = model.name.replace('.gguf', '');
                                                    const isActive = activeModel === modelName;
                                                    return (
                                                        <button
                                                            key={index}
                                                            onClick={() => handleModelSelect(modelName)}
                                                            className={`w-full text-left px-3 py-1.5 rounded-md text-sm transition-colors flex items-center justify-between group
                                                                ${isActive ? 'bg-primary/10 text-primary font-semibold' : 'hover:bg-muted'}`}
                                                        >
                                                            <span className="truncate">{modelName}</span>
                                                            {isActive && <Check className="w-4 h-4 text-primary" />}
                                                        </button>
                                                    );
                                                })
                                            ) : (
                                                <div className="px-3 py-2 text-sm text-muted-foreground text-center">
                                                    No local models found
                                                </div>
                                            )}
                                        </div>
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </div>
                    )}
                </div>

                <div className="flex items-center justify-end gap-2">
                    <button
                        onClick={toggleDarkMode}
                        className="p-2 rounded-md hover:bg-muted transition-colors"
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
                        className="p-2 rounded-md hover:bg-muted transition-colors"
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
