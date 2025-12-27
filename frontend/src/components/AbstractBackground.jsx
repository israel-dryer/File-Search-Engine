import React from 'react';
import { motion } from 'framer-motion';

const AbstractBackground = () => {
    // Generate random shapes
    const shapes = Array.from({ length: 15 }).map((_, i) => ({
        id: i,
        type: ['circle', 'square', 'triangle'][Math.floor(Math.random() * 3)],
        size: Math.random() * 100 + 50, // 50-150px
        x: Math.random() * 100,
        y: Math.random() * 100,
        color: [
            'hsla(221, 83%, 53%, 0.3)', // Primary Blue
            'hsla(262, 83%, 58%, 0.3)', // Purple
            'hsla(320, 70%, 50%, 0.3)', // Pink
            'hsla(180, 70%, 50%, 0.3)'  // Cyan
        ][Math.floor(Math.random() * 4)],
        duration: Math.random() * 10 + 10 // 10-20s
    }));

    return (
        <div className="fixed inset-0 z-0 overflow-hidden pointer-events-none">
            {shapes.map((shape) => (
                <motion.div
                    key={shape.id}
                    className="absolute backdrop-blur-[1px]"
                    style={{
                        left: `${shape.x}%`,
                        top: `${shape.y}%`,
                        width: shape.size,
                        height: shape.size,
                        borderRadius: shape.type === 'circle' ? '50%' : shape.type === 'square' ? '12px' : '0',
                        clipPath: shape.type === 'triangle' ? 'polygon(50% 0%, 0% 100%, 100% 100%)' : 'none',
                        backgroundColor: shape.color,
                    }}
                    animate={{
                        y: [0, -50, 0],
                        rotate: [0, 180, 360],
                        scale: [1, 1.2, 1],
                    }}
                    transition={{
                        duration: shape.duration,
                        repeat: Infinity,
                        ease: "linear"
                    }}
                />
            ))}
        </div>
    );
};

export default AbstractBackground;
