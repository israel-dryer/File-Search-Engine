import React from 'react';
import { ExternalLink, File, ChevronRight, Activity, Sparkles, Bot } from 'lucide-react';
import { motion } from 'framer-motion';
import axios from 'axios';

const SearchResults = ({ results, aiAnswer }) => {
    if (!results.length && !aiAnswer) return null;

    const handleOpenFile = async (filePath) => {
        try {
            await axios.post('http://localhost:8000/api/open-file', { path: filePath });
        } catch (error) {
            console.error('Failed to open file:', error);
        }
    };

    return (
        <div className="w-full max-w-4xl mx-auto mt-12 px-4 pb-20">
            {/* 3D Results Header */}
            <div className="flex items-center justify-between mb-8 px-2">
                <div className="flex items-center gap-2 px-4 py-1.5 rounded-full border border-primary/20 bg-primary/5 shadow-inner">
                    <Activity className="w-4 h-4 text-primary" />
                    <p className="text-xs font-black uppercase tracking-widest text-primary/80">
                        Found <span className="text-primary font-black underline decoration-4 underline-offset-4">{results.length}</span> Objects
                    </p>
                </div>
            </div>

            {/* AI Answer Card - RAG Output */}
            {aiAnswer && (
                <motion.div
                    initial={{ opacity: 0, scale: 0.95, y: -20 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    transition={{ duration: 0.5, ease: "easeOut" }}
                    className="mb-10"
                >
                    <div className="card-3d rounded-3xl overflow-hidden p-1 shadow-primary/20 bg-gradient-to-br from-primary/10 to-transparent border border-primary/20">
                        <div className="glass-v2 rounded-2xl p-6 relative overflow-hidden">
                            {/* Animated Background Glow */}
                            <div className="absolute -top-20 -right-20 w-40 h-40 bg-primary/20 blur-[50px] rounded-full animate-float" />

                            <div className="flex items-center gap-3 mb-4">
                                <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center shadow-lg shadow-primary/30">
                                    <Bot className="w-5 h-5 text-primary-foreground" />
                                </div>
                                <h3 className="text-lg font-bold text-3d tracking-tight">Nexus AI Insight</h3>
                            </div>

                            <div className="prose prose-invert max-w-none">
                                <p className="text-base sm:text-lg text-foreground/90 font-medium leading-relaxed">
                                    {aiAnswer}
                                </p>
                            </div>

                            <div className="mt-4 pt-4 border-t border-border/50 flex items-center gap-2">
                                <Sparkles className="w-3 h-3 text-primary animate-pulse" />
                                <span className="text-[10px] uppercase font-black tracking-widest text-muted-foreground">Generated from context</span>
                            </div>
                        </div>
                    </div>
                </motion.div>
            )}

            {/* 3D Card List */}
            <div className="space-y-6">
                {results.map((result, index) => (
                    <motion.div
                        key={index}
                        initial={{ opacity: 0, scale: 0.9, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        transition={{ duration: 0.4, delay: index * 0.1, ease: "easeOut" }}
                    >
                        <div className="card-3d card-hover-effect rounded-3xl overflow-hidden active:scale-95 transition-transform duration-150">
                            {/* File Bar - Elevated 3D header */}
                            {result.file_name && (
                                <div className="flex items-center justify-between px-6 py-4 bg-muted/40 border-b border-border/50">
                                    <button
                                        onClick={() => handleOpenFile(result.file_path)}
                                        className="flex items-center gap-4 text-sm font-bold text-foreground hover:text-primary transition-all group/file"
                                    >
                                        <div className="w-10 h-10 rounded-2xl bg-primary shadow-lg shadow-primary/20 flex items-center justify-center group-hover/file:scale-110 transition-transform duration-300">
                                            <File className="w-5 h-5 text-primary-foreground" />
                                        </div>
                                        <div className="flex flex-col items-start leading-none">
                                            <span className="text-base tracking-tight truncate">{result.file_name}</span>
                                            <span className="text-[10px] uppercase font-black opacity-30 tracking-widest pt-1">Reference ID: {result.faiss_idx || 'N/A'}</span>
                                        </div>
                                    </button>
                                    <div className="w-8 h-8 rounded-full flex items-center justify-center bg-background border border-border shadow-md">
                                        <ChevronRight className="w-4 h-4 text-muted-foreground" />
                                    </div>
                                </div>
                            )}

                            {/* Main Body */}
                            <div className="p-6">
                                {/* Context */}
                                <div className="relative">
                                    <p className="text-sm font-medium text-muted-foreground/80 leading-relaxed line-clamp-3 pl-4 border-l border-border italic">
                                        {result.document}
                                    </p>
                                </div>

                                {/* Physical Tag Cloud */}
                                {result.tags && result.tags.length > 0 && (
                                    <div className="flex flex-wrap gap-2 mt-6">
                                        {result.tags.map((tag, i) => (
                                            <span
                                                key={i}
                                                className="px-3 py-1.5 rounded-xl text-[10px] font-black uppercase tracking-widest bg-muted border border-border shadow-sm hover:scale-110 hover:shadow-md hover:bg-primary hover:text-primary-foreground transition-all cursor-default"
                                            >
                                                {tag}
                                            </span>
                                        ))}
                                    </div>
                                )}
                            </div>
                        </div>
                    </motion.div>
                ))}
            </div>
        </div>
    );
};

export default SearchResults;
