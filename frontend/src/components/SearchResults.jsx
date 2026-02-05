import React, { useMemo } from 'react';
import { ExternalLink, File, Sparkles, FileText, Image, Table, Presentation, Brain } from 'lucide-react';
import { motion } from 'framer-motion';
import axios from 'axios';

const getFileIcon = (fileName) => {
    const ext = fileName?.split('.').pop()?.toLowerCase();
    switch (ext) {
        case 'pdf': return <FileText className="w-4 h-4 text-red-400" />;
        case 'docx':
        case 'doc': return <FileText className="w-4 h-4 text-blue-400" />;
        case 'xlsx':
        case 'xls': return <Table className="w-4 h-4 text-green-400" />;
        case 'pptx':
        case 'ppt': return <Presentation className="w-4 h-4 text-orange-400" />;
        case 'png':
        case 'jpg':
        case 'jpeg': return <Image className="w-4 h-4 text-purple-400" />;
        default: return <File className="w-4 h-4 text-muted-foreground" />;
    }
};

const handleOpenFile = async (filePath) => {
    try {
        await axios.post('http://localhost:8000/api/open-file', { path: filePath });
    } catch (error) {
        console.error('Failed to open file:', error);
    }
};

const SearchResults = ({ results, aiAnswer }) => {
    if (!results.length && !aiAnswer) return null;

    const resultsList = useMemo(() => {
        return results.map((result, index) => (
            <motion.div
                key={index}
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: index * 0.05 }}
                className="result-card group/card cursor-pointer hover:ring-2 hover:ring-primary/50 focus-visible:ring-2 focus-visible:ring-primary/50 focus-visible:outline-none transition-all"
                onClick={() => result.file_path && handleOpenFile(result.file_path)}
                role="button"
                tabIndex={0}
                aria-label={`Open ${result.file_name}`}
                onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        result.file_path && handleOpenFile(result.file_path);
                    }
                }}
            >
                {/* File Header */}
                {result.file_name && (
                    <div className="flex items-center justify-between px-4 py-3 border-b border-border/50 bg-secondary/20 group-hover/card:bg-secondary/30 transition-colors">
                        <div className="flex items-center gap-3 text-sm font-medium text-foreground/90">
                            <div className="p-1.5 rounded-lg bg-secondary/50 transition-colors">
                                {getFileIcon(result.file_name)}
                            </div>
                            <span className="truncate max-w-[300px]">{result.file_name}</span>
                        </div>
                        <button
                            onClick={(e) => {
                                e.stopPropagation();
                                handleOpenFile(result.file_path);
                            }}
                            className="p-2 rounded-lg hover:bg-secondary transition-colors text-muted-foreground hover:text-foreground"
                            title="Open file externally"
                            aria-label="Open file externally"
                        >
                            <ExternalLink className="w-4 h-4" />
                        </button>
                    </div>
                )}

                {/* Content Preview */}
                <div className="p-4">
                    <p className="text-sm text-foreground/80 leading-relaxed line-clamp-4">
                        {result.document}
                    </p>

                    {/* Tags */}
                    {/* Tags Removed per user request */}
                </div>
            </motion.div>
        ));
    }, [results]);

    return (
        <div className="w-full mt-8 pb-20">
            <div className="flex gap-6">
                {/* Main Results Column */}
                <div className="flex-1 space-y-4">
                    {resultsList}
                </div>

                {/* AI Insights Sidebar */}
                {aiAnswer && (
                    <motion.aside
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.4, delay: 0.2 }}
                        className="hidden lg:block w-80 flex-shrink-0"
                    >
                        <div className="sticky top-24 ai-panel rounded-2xl p-5">
                            {/* Header */}
                            <div className="flex items-center gap-3 mb-4 pb-4 border-b border-primary/20">
                                <div className="p-2 rounded-xl bg-gradient-to-br from-primary/20 to-accent/20">
                                    <Brain className="w-5 h-5 text-primary" />
                                </div>
                                <div>
                                    <h3 className="text-sm font-bold">AI Insights</h3>
                                    <p className="text-xs text-muted-foreground">Powered by local LLM</p>
                                </div>
                            </div>

                            {/* Answer Content */}
                            <div className="prose prose-sm max-w-none text-foreground/85 leading-relaxed">
                                <p>{aiAnswer}</p>
                            </div>

                            {/* Decorative Glow */}
                            <div className="absolute -inset-1 bg-gradient-to-r from-primary/20 via-accent/20 to-primary/20 rounded-2xl blur-xl opacity-30 -z-10" />
                        </div>
                    </motion.aside>
                )}
            </div>

            {/* Mobile AI Answer (shown on small screens) */}
            {aiAnswer && (
                <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                    className="lg:hidden mb-6 ai-panel rounded-2xl p-4"
                >
                    <div className="flex items-center gap-3 mb-3">
                        <div className="p-2 rounded-xl bg-gradient-to-br from-primary/20 to-accent/20">
                            <Sparkles className="w-4 h-4 text-primary" />
                        </div>
                        <h3 className="text-sm font-bold">AI Insights</h3>
                    </div>
                    <p className="text-sm text-foreground/80">{aiAnswer}</p>
                </motion.div>
            )}
        </div>
    );
};

export default SearchResults;
