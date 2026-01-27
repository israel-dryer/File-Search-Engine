import axios from 'axios';

const API_URL = 'http://localhost:8000/api/logs';

const logger = {
    log: async (level, message, stack = null) => {
        // Always log to console for development
        console.log(`[${level.toUpperCase()}] ${message}`);
        if (stack) console.error(stack);

        try {
            await axios.post(API_URL, {
                level,
                message: typeof message === 'string' ? message : JSON.stringify(message),
                source: "Frontend",
                stack: stack ? stack.toString() : null
            });
        } catch (err) {
            // Prevent infinite loops if logging fails
            console.error("Failed to send log to backend:", err);
        }
    },

    info: (message) => logger.log('info', message),
    warn: (message) => logger.log('warn', message),
    error: (message, stack = null) => logger.log('error', message, stack),

    init: () => {
        window.onerror = (message, source, lineno, colno, error) => {
            const stack = error ? error.stack : `${source}:${lineno}:${colno}`;
            logger.error(`Global Error: ${message}`, stack);
        };

        window.onunhandledrejection = (event) => {
            logger.error(`Unhandled Promise Rejection: ${event.reason}`, event.reason ? event.reason.stack : null);
        };

        logger.info("Frontend logger initialized");
    }
};

export default logger;
