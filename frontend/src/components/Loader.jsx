import React from 'react';

export const Loader = () => (
    <div className="relative w-16 h-16">
        <div className="absolute inset-0 rounded-full border-4 border-primary/20 blur-sm"></div>
        <div className="absolute inset-0 rounded-full border-4 border-t-primary animate-spin"></div>
        <div className="absolute inset-4 rounded-full bg-primary/10 backdrop-blur-md animate-pulse"></div>
    </div>
);
