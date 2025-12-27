import React from 'react';
import { motion } from 'framer-motion';

const AnimatedText = ({ text, className = "" }) => {
    // Split text into words and then characters to handle spaces correctly
    const words = text.split(" ");

    const container = {
        hidden: { opacity: 0 },
        visible: (i = 1) => ({
            opacity: 1,
            transition: { staggerChildren: 0.05, delayChildren: 0.04 * i },
        }),
    };

    const child = {
        visible: {
            opacity: 1,
            y: 0,
            x: 0,
            rotate: 0,
            transition: {
                type: "spring",
                damping: 12,
                stiffness: 100,
            },
        },
        hidden: {
            opacity: 0,
            y: 20,
            rotate: 10,
        },
    };

    return (
        <motion.div
            style={{ display: "flex", flexWrap: "wrap", justifyContent: "center" }}
            variants={container}
            initial="hidden"
            animate="visible"
            className={className}
        >
            {words.map((word, index) => (
                <div key={index} style={{ display: "flex", marginRight: "0.25em" }}>
                    {Array.from(word).map((character, charIndex) => (
                        <motion.span variants={child} key={charIndex}>
                            {character}
                        </motion.span>
                    ))}
                </div>
            ))}
        </motion.div>
    );
};

export default AnimatedText;
