import React, { useEffect, useRef, useState } from 'react';

/**
 * CosmicBackground - Creates an animated cosmic nebula background
 * Adapts to light/dark mode with different color schemes
 */
const CosmicBackground = () => {
    const canvasRef = useRef(null);
    const [isDark, setIsDark] = useState(true);

    // Watch for theme changes
    useEffect(() => {
        const checkTheme = () => {
            setIsDark(document.documentElement.classList.contains('dark'));
        };

        checkTheme();

        // Observe class changes on documentElement
        const observer = new MutationObserver(checkTheme);
        observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });

        return () => observer.disconnect();
    }, []);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        let animationId;
        let particles = [];

        const resizeCanvas = () => {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        };

        // Create particles with theme-aware colors
        const createParticles = () => {
            particles = [];
            const particleCount = 80;
            for (let i = 0; i < particleCount; i++) {
                particles.push({
                    x: Math.random() * canvas.width,
                    y: Math.random() * canvas.height,
                    size: Math.random() * 3 + 1,
                    speedX: (Math.random() - 0.5) * 0.5,
                    speedY: (Math.random() - 0.5) * 0.5,
                    opacity: Math.random() * 0.5 + 0.2,
                    hue: Math.random() > 0.5 ? 260 : 220 // Purple or Blue
                });
            }
        };

        // Draw particles
        const drawParticles = () => {
            particles.forEach(p => {
                const lightness = isDark ? 70 : 50;
                const saturation = isDark ? 80 : 60;

                ctx.beginPath();
                ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
                ctx.fillStyle = `hsla(${p.hue}, ${saturation}%, ${lightness}%, ${p.opacity})`;
                ctx.fill();

                // Add glow effect
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.size * 2, 0, Math.PI * 2);
                ctx.fillStyle = `hsla(${p.hue}, ${saturation}%, ${lightness}%, ${p.opacity * 0.3})`;
                ctx.fill();

                // Update position
                p.x += p.speedX;
                p.y += p.speedY;

                // Wrap around screen
                if (p.x < 0) p.x = canvas.width;
                if (p.x > canvas.width) p.x = 0;
                if (p.y < 0) p.y = canvas.height;
                if (p.y > canvas.height) p.y = 0;
            });
        };

        // Animation loop
        const animate = () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            drawParticles();
            animationId = requestAnimationFrame(animate);
        };

        resizeCanvas();
        createParticles();
        animate();

        window.addEventListener('resize', () => {
            resizeCanvas();
            createParticles();
        });

        return () => {
            cancelAnimationFrame(animationId);
            window.removeEventListener('resize', resizeCanvas);
        };
    }, [isDark]);

    // Theme-dependent colors
    const darkGradient = 'linear-gradient(135deg, #0a0015 0%, #1a0a2e 25%, #0d1b2a 50%, #1b2838 75%, #0a0015 100%)';
    const lightGradient = 'linear-gradient(135deg, #e8e4f0 0%, #dcd8f5 25%, #e0e8f8 50%, #f0f0fa 75%, #e8e4f0 100%)';

    const orbColors = isDark ? {
        orb1: 'radial-gradient(circle, rgba(139, 92, 246, 0.4) 0%, rgba(139, 92, 246, 0.1) 40%, transparent 70%)',
        orb2: 'radial-gradient(circle, rgba(59, 130, 246, 0.4) 0%, rgba(59, 130, 246, 0.1) 40%, transparent 70%)',
        orb3: 'radial-gradient(circle, rgba(167, 139, 250, 0.3) 0%, rgba(167, 139, 250, 0.05) 50%, transparent 70%)',
        orb4: 'radial-gradient(circle, rgba(34, 211, 238, 0.25) 0%, transparent 60%)',
    } : {
        orb1: 'radial-gradient(circle, rgba(139, 92, 246, 0.25) 0%, rgba(139, 92, 246, 0.05) 40%, transparent 70%)',
        orb2: 'radial-gradient(circle, rgba(59, 130, 246, 0.25) 0%, rgba(59, 130, 246, 0.05) 40%, transparent 70%)',
        orb3: 'radial-gradient(circle, rgba(167, 139, 250, 0.2) 0%, rgba(167, 139, 250, 0.03) 50%, transparent 70%)',
        orb4: 'radial-gradient(circle, rgba(34, 211, 238, 0.15) 0%, transparent 60%)',
    };

    return (
        <div className="cosmic-bg-container" style={{
            position: 'fixed',
            inset: 0,
            overflow: 'hidden',
            pointerEvents: 'none',
            zIndex: 0,
            transition: 'background 0.5s ease-in-out'
        }}>
            {/* Base gradient - changes with theme */}
            <div style={{
                position: 'absolute',
                inset: 0,
                background: isDark ? darkGradient : lightGradient,
                transition: 'background 0.5s ease-in-out'
            }} />

            {/* Nebula Orb 1 - Large Purple */}
            <div style={{
                position: 'absolute',
                top: '-20%',
                left: '-10%',
                width: '60vw',
                height: '60vw',
                borderRadius: '50%',
                background: orbColors.orb1,
                filter: 'blur(60px)',
                animation: 'float1 20s ease-in-out infinite',
                transition: 'background 0.5s ease-in-out'
            }} />

            {/* Nebula Orb 2 - Electric Blue */}
            <div style={{
                position: 'absolute',
                bottom: '-30%',
                right: '-10%',
                width: '50vw',
                height: '50vw',
                borderRadius: '50%',
                background: orbColors.orb2,
                filter: 'blur(80px)',
                animation: 'float2 25s ease-in-out infinite',
                transition: 'background 0.5s ease-in-out'
            }} />

            {/* Nebula Orb 3 - Violet accent */}
            <div style={{
                position: 'absolute',
                top: '30%',
                right: '10%',
                width: '35vw',
                height: '35vw',
                borderRadius: '50%',
                background: orbColors.orb3,
                filter: 'blur(50px)',
                animation: 'float3 18s ease-in-out infinite',
                transition: 'background 0.5s ease-in-out'
            }} />

            {/* Nebula Orb 4 - Cyan highlight */}
            <div style={{
                position: 'absolute',
                top: '60%',
                left: '20%',
                width: '25vw',
                height: '25vw',
                borderRadius: '50%',
                background: orbColors.orb4,
                filter: 'blur(40px)',
                animation: 'float4 22s ease-in-out infinite',
                transition: 'background 0.5s ease-in-out'
            }} />

            {/* Particle canvas */}
            <canvas
                ref={canvasRef}
                style={{
                    position: 'absolute',
                    inset: 0,
                    zIndex: 1,
                }}
            />

            {/* Grid overlay for texture */}
            <div style={{
                position: 'absolute',
                inset: 0,
                backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='60' height='60'%3E%3Cpath d='M0 0h60v60H0z' fill='none'/%3E%3Cpath d='M0 60h60M60 0v60' stroke='${isDark ? 'white' : 'black'}' stroke-opacity='0.03'/%3E%3C/svg%3E")`,
                opacity: 0.5,
            }} />

            {/* CSS Keyframes */}
            <style>{`
                @keyframes float1 {
                    0%, 100% { transform: translate(0, 0) scale(1); }
                    50% { transform: translate(5%, 10%) scale(1.1); }
                }
                @keyframes float2 {
                    0%, 100% { transform: translate(0, 0) scale(1); }
                    50% { transform: translate(-8%, -5%) scale(1.05); }
                }
                @keyframes float3 {
                    0%, 100% { transform: translate(0, 0); }
                    50% { transform: translate(-10%, 15%); }
                }
                @keyframes float4 {
                    0%, 100% { transform: translate(0, 0) scale(1); }
                    50% { transform: translate(10%, -10%) scale(1.15); }
                }
            `}</style>
        </div>
    );
};

export default CosmicBackground;
