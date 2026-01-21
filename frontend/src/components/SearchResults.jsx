import React from 'react';
import { ExternalLink, File, Sparkles } from 'lucide-react';
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
        <div className="w-full max-w-3xl mx-auto mt-8 pb-20">

            {aiAnswer && (
                <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                    className="mb-8 p-4 bg-secondary/50 rounded-lg border border-border"
                >
                    <div className="flex items-start gap-3 mb-3">
                        <div className="flex-shrink-0 pt-0.5">
                            <Sparkles className="w-5 h-5 text-primary" />
                        </div>
                        <h3 className="text-md font-semibold text-foreground">AI Answer</h3>
                    </div>
                    <div className="prose prose-sm max-w-none text-foreground/80">
                        <p>{aiAnswer}</p>
                    </div>
                </motion.div>
            )}

            <div className="space-y-4">
                {results.map((result, index) => (
                    <motion.div
                        key={index}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.3, delay: index * 0.05 }}
                        className="border border-border rounded-lg overflow-hidden transition-colors hover:bg-secondary/50"
                    >
                        {result.file_name && (
                            <div className="flex items-center justify-between px-4 py-2 bg-secondary/30 border-b border-border">
                                <button
                                    onClick={() => handleOpenFile(result.file_path)}
                                    className="flex items-center gap-2 text-sm font-medium hover:text-primary transition-colors group"
                                >
                                    <File className="w-4 h-4 text-muted-foreground group-hover:text-primary" />
                                    <span className="truncate">{result.file_name}</span>
                                </button>
                                <button onClick={() => handleOpenFile(result.file_path)} className="p-1.5 rounded-md hover:bg-muted">
                                    <ExternalLink className="w-4 h-4 text-muted-foreground" />
                                </button>
                            </div>
                        )}

                        <div className="p-4">
                            <p className="text-sm text-foreground/80 leading-relaxed">
                                {result.document}
                            </p>

                            {result.tags && result.tags.length > 0 && (
                                <div className="flex flex-wrap gap-2 mt-4">
                                    {result.tags.map((tag, i) => (
                                        <span
                                            key={i}
                                            className="px-2 py-0.5 rounded text-xs font-medium bg-muted text-muted-foreground border border-border"
                                        >
                                            {tag}
                                        </span>
                                    ))}
                                </div>
                            )}
                        </div>
                    </motion.div>
                ))}
            </div>
        </div>
    );
};

export default SearchResults;
