import React, { useEffect, useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Bot, Terminal, Cpu, Database, FileText, CheckCircle2, AlertCircle, ArrowRight, Sparkles } from 'lucide-react';

const AgentChat = ({ query }) => {
    const [events, setEvents] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const scrollRef = useRef(null);

    useEffect(() => {
        if (!query) return;

        setEvents([]);
        setIsLoading(true);

        const evtSource = new EventSource(`http://localhost:8000/api/agent/chat?query=${encodeURIComponent(query)}`);

        evtSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);

                if (data.type === 'error') {
                    setEvents(prev => [...prev, { ...data, timestamp: Date.now() }]);
                    evtSource.close();
                    setIsLoading(false);
                } else if (data.type === 'answer') {
                    setEvents(prev => [...prev, { ...data, timestamp: Date.now() }]);
                    evtSource.close();
                    setIsLoading(false);
                } else {
                    setEvents(prev => [...prev, { ...data, timestamp: Date.now() }]);
                }
            } catch (e) {
                console.error("Parse error", e);
            }
        };

        evtSource.onerror = (err) => {
            console.error("EventSource failed:", err);
            evtSource.close();
            setIsLoading(false);
        };

        return () => {
            evtSource.close();
        };
    }, [query]);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [events]);

    const getIcon = (type) => {
        switch (type) {
            case 'thought': return <Cpu className="w-4 h-4 text-blue-400" />;
            case 'action': return <Terminal className="w-4 h-4 text-orange-400" />;
            case 'observation': return <Database className="w-4 h-4 text-green-400" />;
            case 'answer': return <CheckCircle2 className="w-5 h-5 text-primary" />;
            case 'error': return <AlertCircle className="w-5 h-5 text-red-500" />;
            default: return <Bot className="w-4 h-4" />;
        }
    };

    return (
        <div className="w-full max-w-4xl mx-auto mt-8 px-4 pb-20">
            <div className="flex items-center gap-3 mb-6 px-4">
                <div className="w-10 h-10 rounded-2xl bg-primary/20 flex items-center justify-center border border-primary/30 animate-pulse">
                    <Bot className="w-6 h-6 text-primary" />
                </div>
                <div>
                    <h2 className="text-xl font-bold tracking-tight">Agent Reasoning</h2>
                    <p className="text-xs font-mono text-muted-foreground uppercase tracking-widest">RAPTOR + ReAct Powered</p>
                </div>
            </div>

            <div className="space-y-4">
                <AnimatePresence>
                    {events.map((event, index) => (
                        <motion.div
                            key={index}
                            initial={{ opacity: 0, y: 10, scale: 0.98 }}
                            animate={{ opacity: 1, y: 0, scale: 1 }}
                            transition={{ duration: 0.3 }}
                            className={`rounded-2xl border backdrop-blur-sm shadow-sm overflow-hidden 
                                ${event.type === 'answer' ? 'bg-primary/10 border-primary/30 shadow-primary/10' :
                                    event.type === 'observation' ? 'bg-black/20 border-white/5 mx-4' :
                                        'bg-card/40 border-border/50'}`}
                        >
                            {event.type === 'answer' ? (
                                <div className="p-6">
                                    <div className="flex items-center gap-2 mb-4 text-primary">
                                        <Sparkles className="w-5 h-5" />
                                        <span className="text-xs font-black uppercase tracking-widest">Final Conclusion</span>
                                    </div>
                                    <div className="prose prose-invert max-w-none text-lg leading-relaxed">
                                        {event.content}
                                    </div>
                                </div>
                            ) : (
                                <div className="p-4 flex gap-4">
                                    <div className="mt-1 shrink-0 opacity-70">
                                        {getIcon(event.type)}
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center gap-2 mb-1 opacity-50">
                                            <span className="text-[10px] uppercase font-bold tracking-wider">{event.type}</span>
                                        </div>
                                        <div className={`text-sm ${event.type === 'observation' ? 'font-mono text-xs opacity-70' : 'font-medium'}`}>
                                            {event.content}
                                        </div>
                                    </div>
                                </div>
                            )}
                        </motion.div>
                    ))}
                </AnimatePresence>

                {isLoading && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="flex items-center gap-3 px-6 py-4 text-muted-foreground/60 animate-pulse"
                    >
                        <div className="w-2 h-2 rounded-full bg-current animate-bounce" />
                        <div className="w-2 h-2 rounded-full bg-current animate-bounce delay-100" />
                        <div className="w-2 h-2 rounded-full bg-current animate-bounce delay-200" />
                        <span className="text-xs font-mono uppercase tracking-widest ml-2">Thinking</span>
                    </motion.div>
                )}

                <div ref={scrollRef} />
            </div>
        </div>
    );
};

export default AgentChat;
