/**
 * Unified Startup Script for File Search Engine
 * Starts both backend (FastAPI) and frontend (Vite) with health checks
 */

const { spawn, exec } = require('child_process');
const http = require('http');
const path = require('path');

const BACKEND_PORT = 8000;
const FRONTEND_PORT = 5173;
const HEALTH_CHECK_INTERVAL = 1000;
const HEALTH_CHECK_TIMEOUT = 60000;

const colors = {
    reset: '\x1b[0m',
    bright: '\x1b[1m',
    red: '\x1b[31m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    magenta: '\x1b[35m',
    cyan: '\x1b[36m'
};

function log(prefix, color, message) {
    const timestamp = new Date().toLocaleTimeString();
    console.log(`${colors.bright}[${timestamp}]${colors.reset} ${color}[${prefix}]${colors.reset} ${message}`);
}

function checkPort(port) {
    return new Promise((resolve) => {
        const server = require('net').createServer();
        server.once('error', () => resolve(false));
        server.once('listening', () => {
            server.close();
            resolve(true);
        });
        server.listen(port);
    });
}

function healthCheck(port, path = '/') {
    return new Promise((resolve) => {
        const req = http.get(`http://localhost:${port}${path}`, (res) => {
            resolve(res.statusCode >= 200 && res.statusCode < 400);
        });
        req.on('error', () => resolve(false));
        req.setTimeout(2000, () => {
            req.destroy();
            resolve(false);
        });
    });
}

async function waitForService(name, port, checkPath, timeout) {
    const startTime = Date.now();
    while (Date.now() - startTime < timeout) {
        const isReady = await healthCheck(port, checkPath);
        if (isReady) {
            return true;
        }
        await new Promise(r => setTimeout(r, HEALTH_CHECK_INTERVAL));
    }
    return false;
}

function openBrowser(url) {
    const platform = process.platform;
    let cmd;
    if (platform === 'win32') {
        cmd = `start ${url}`;
    } else if (platform === 'darwin') {
        cmd = `open ${url}`;
    } else {
        cmd = `xdg-open ${url}`;
    }
    exec(cmd, (err) => {
        if (err) log('Browser', colors.yellow, 'Could not open browser automatically');
    });
}

async function main() {
    console.log('\n' + colors.bright + colors.cyan + '═'.repeat(60) + colors.reset);
    console.log(colors.bright + colors.cyan + '  FILE SEARCH ENGINE - Unified Startup' + colors.reset);
    console.log(colors.bright + colors.cyan + '═'.repeat(60) + colors.reset + '\n');

    // Check port availability
    log('Setup', colors.yellow, 'Checking port availability...');

    const backendPortFree = await checkPort(BACKEND_PORT);
    const frontendPortFree = await checkPort(FRONTEND_PORT);

    if (!backendPortFree) {
        log('Error', colors.red, `Port ${BACKEND_PORT} is already in use. Please stop any existing backend process.`);
        process.exit(1);
    }
    if (!frontendPortFree) {
        log('Error', colors.red, `Port ${FRONTEND_PORT} is already in use. Please stop any existing frontend process.`);
        process.exit(1);
    }

    log('Setup', colors.green, 'Ports available ✓');

    // Detect Python executable (check for venv)
    const isWin = process.platform === 'win32';
    const venvPython = isWin
        ? path.join(__dirname, '..', 'venv_new', 'Scripts', 'python.exe')
        : path.join(__dirname, '..', 'venv_new', 'bin', 'python');

    const fs = require('fs');
    const pythonExe = fs.existsSync(venvPython) ? venvPython : 'python';
    log('Setup', colors.cyan, `Using Python executable: ${pythonExe}`);

    // Start Backend
    log('Backend', colors.blue, 'Starting FastAPI server...');
    const backendProcess = spawn(pythonExe, ['-m', 'uvicorn', 'backend.api:app', '--reload', '--host', '0.0.0.0', '--port', String(BACKEND_PORT)], {
        cwd: path.resolve(__dirname, '..'),
        shell: true,
        stdio: ['ignore', 'pipe', 'pipe']
    });

    backendProcess.stdout.on('data', (data) => {
        const lines = data.toString().split('\n').filter(l => l.trim());
        lines.forEach(line => log('Backend', colors.blue, line));
    });

    backendProcess.stderr.on('data', (data) => {
        const lines = data.toString().split('\n').filter(l => l.trim());
        lines.forEach(line => log('Backend', colors.blue, line));
    });

    // Start Frontend
    log('Frontend', colors.magenta, 'Starting Vite dev server...');
    const npmCmd = isWin ? 'npm.cmd' : 'npm';
    const frontendProcess = spawn(npmCmd, ['run', 'dev'], {
        cwd: path.resolve(__dirname, '..', 'frontend'),
        shell: true,
        stdio: ['ignore', 'pipe', 'pipe']
    });

    frontendProcess.stdout.on('data', (data) => {
        const lines = data.toString().split('\n').filter(l => l.trim());
        lines.forEach(line => log('Frontend', colors.magenta, line));
    });

    frontendProcess.stderr.on('data', (data) => {
        const lines = data.toString().split('\n').filter(l => l.trim());
        lines.forEach(line => log('Frontend', colors.magenta, line));
    });

    // Wait for services to be ready
    log('Health', colors.yellow, 'Waiting for services to become healthy...');

    const [backendReady, frontendReady] = await Promise.all([
        waitForService('Backend', BACKEND_PORT, '/api/config', HEALTH_CHECK_TIMEOUT),
        waitForService('Frontend', FRONTEND_PORT, '/', HEALTH_CHECK_TIMEOUT)
    ]);

    if (!backendReady) {
        log('Error', colors.red, 'Backend failed to start within timeout');
    } else {
        log('Backend', colors.green, `Ready at http://localhost:${BACKEND_PORT} ✓`);
    }

    if (!frontendReady) {
        log('Error', colors.red, 'Frontend failed to start within timeout');
    } else {
        log('Frontend', colors.green, `Ready at http://localhost:${FRONTEND_PORT} ✓`);
    }

    if (backendReady && frontendReady) {
        console.log('\n' + colors.bright + colors.green + '═'.repeat(60) + colors.reset);
        console.log(colors.bright + colors.green + '  ✓ All services are running!' + colors.reset);
        console.log(colors.bright + colors.green + '  Open: http://localhost:' + FRONTEND_PORT + colors.reset);
        console.log(colors.bright + colors.green + '═'.repeat(60) + colors.reset + '\n');

        // Open browser
        openBrowser(`http://localhost:${FRONTEND_PORT}`);
    }

    // Handle graceful shutdown
    const shutdown = () => {
        log('Shutdown', colors.yellow, 'Stopping services...');
        backendProcess.kill();
        frontendProcess.kill();
        process.exit(0);
    };

    process.on('SIGINT', shutdown);
    process.on('SIGTERM', shutdown);

    // Keep the process running
    backendProcess.on('exit', (code) => {
        log('Backend', colors.red, `Process exited with code ${code}`);
    });

    frontendProcess.on('exit', (code) => {
        log('Frontend', colors.red, `Process exited with code ${code}`);
    });
}

main().catch(err => {
    log('Error', colors.red, err.message);
    process.exit(1);
});
