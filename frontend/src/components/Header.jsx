import React, { useState } from 'react';
import { Settings, Moon, Sun, Box, Cpu, ChevronDown, Check } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const Header = ({ darkMode, toggleDarkMode, openSettings, activeModel, availableModels = [], onModelChange }) => {
    const [isModelDropdownOpen, setIsModelDropdownOpen] = useState(false);

    const toggleModelDropdown = () => {
        setIsModelDropdownOpen(!isModelDropdownOpen);
    };

    const handleModelSelect = (modelName) => {
        onModelChange(modelName);
        setIsModelDropdownOpen(false);
    };

    return (
        <header className="sticky top-0 z-40 w-full border-b border-border/50 glass-v2">
            <div className="container flex h-16 items-center justify-between px-4 max-w-7xl mx-auto">
                <div className="flex items-center gap-3 group cursor-pointer">
                    <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center shadow-lg shadow-primary/20 transform-gpu group-hover:rotate-12 group-hover:scale-110 transition-transform duration-300">
                        <Box className="w-5 h-5 text-primary-foreground" />
                    </div>
                    <div className="flex flex-col leading-none">
                        <span className="text-xl font-extrabold tracking-tighter text-3d py-1 uppercase scale-90 -ml-1">
                            File Search
                        </span>
                    </div>
                </div>

                <div className="flex items-center gap-2 sm:gap-4">
                    {/* Active Model Dropdown */}
                    {activeModel && (
                        <div className="relative">
                            <button
                                onClick={toggleModelDropdown}
                                className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-secondary/50 border border-border/50 shadow-inner hover:bg-secondary transition-colors"
                            >
                                <Cpu className="w-3.5 h-3.5 text-primary animate-pulse" />
                                <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground truncate max-w-[150px]">
                                    {activeModel}
                                </span>
                                <ChevronDown className={`w-3 h-3 text-muted-foreground transition-transform duration-300 ${isModelDropdownOpen ? 'rotate-180' : ''}`} />
                            </button>

                            <AnimatePresence>
                                {isModelDropdownOpen && (
                                    <motion.div
                                        initial={{ opacity: 0, y: 10, scale: 0.95 }}
                                        animate={{ opacity: 1, y: 0, scale: 1 }}
                                        exit={{ opacity: 0, y: 10, scale: 0.95 }}
                                        className="absolute right-0 mt-2 w-64 p-1 rounded-xl bg-popover border border-border/50 shadow-2xl z-50 overflow-hidden backdrop-blur-xl"
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
                                                            className={`w-full text-left px-3 py-2 rounded-lg text-xs font-medium transition-colors flex items-center justify-between group
                                                                ${isActive ? 'bg-primary/10 text-primary' : 'text-foreground hover:bg-muted'}`}
                                                        >
                                                            <span className="truncate">{modelName}</span>
                                                            {isActive && <Check className="w-3 h-3 text-primary" />}
                                                        </button>
                                                    );
                                                })
                                            ) : (
                                                <div className="px-3 py-2 text-xs text-muted-foreground text-center">
                                                    No local models found
                                                </div>
                                            )}
                                        </div>
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </div>
                    )}

                    <div className="flex items-center gap-2">
                        <button
                            onClick={toggleDarkMode}
                            className="p-2.5 rounded-xl hover:bg-muted transition-all duration-300 hover:scale-110 active:scale-95 shadow-lg border border-transparent hover:border-border"
                            aria-label="Toggle theme"
                        >
                            {darkMode ? (
                                <Sun className="w-5 h-5 text-yellow-500" />
                            ) : (
                                <Moon className="w-5 h-5 text-primary" />
                            )}
                        </button>
                        <button
                            onClick={openSettings}
                            className="p-2.5 rounded-xl hover:bg-muted transition-all duration-300 hover:scale-110 active:scale-95 shadow-lg border border-transparent hover:border-border"
                            aria-label="Settings"
                        >
                            <Settings className="w-5 h-5" />
                        </button>
                    </div>
                </div>
            </div>
        </header>
    );
};

export default Header;
