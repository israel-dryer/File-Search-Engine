import React from 'react';

export const AppLogo = ({ className = "w-10 h-10" }) => (
    <svg viewBox="0 0 100 100" className={className} fill="none" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="hsl(221, 83%, 53%)" />
                <stop offset="100%" stopColor="hsl(217, 91%, 60%)" />
            </linearGradient>
            <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="5" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
        </defs>

        {/* Background Document Shape */}
        <rect x="20" y="15" width="45" height="60" rx="8" fill="currentColor" fillOpacity="0.1" stroke="currentColor" strokeWidth="2" />
        <path d="M65 15 L65 30 L80 30" fill="none" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" />

        {/* Magnifying Glass (Main Element) */}
        <circle cx="55" cy="55" r="20" stroke="url(#logoGradient)" strokeWidth="6" fill="none" filter="url(#glow)" />
        <path d="M70 70 L85 85" stroke="url(#logoGradient)" strokeWidth="6" strokeLinecap="round" />

        {/* AI Sparkle */}
        <path d="M45 45 L50 35 L55 45 L65 50 L55 55 L50 65 L45 55 L35 50 Z" fill="white" className="animate-pulse" />
    </svg>
);
