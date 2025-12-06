#!/usr/bin/env node

/**
 * SmartMemory MCP Server Launcher
 * 
 * This script launches the Python-based SmartMemory MCP server.
 * It requires Python 3.11+ and the smart_memory package to be installed.
 */

const { spawn } = require('child_process');
const path = require('path');

// Find python3 or python
function findPython() {
    const pythonCommands = ['python3', 'python'];

    for (const cmd of pythonCommands) {
        try {
            const result = require('child_process').spawnSync(cmd, ['--version'], {
                encoding: 'utf8',
                stdio: 'pipe'
            });

            if (result.status === 0) {
                const version = result.stdout || result.stderr;
                const match = version.match(/Python (\d+)\.(\d+)/);
                if (match) {
                    const major = parseInt(match[1]);
                    const minor = parseInt(match[2]);
                    if (major === 3 && minor >= 11) {
                        return cmd;
                    }
                }
            }
        } catch (e) {
            continue;
        }
    }

    return null;
}

// Check if smart_memory is installed
function checkSmartMemoryInstalled(pythonCmd) {
    try {
        const result = require('child_process').spawnSync(
            pythonCmd,
            ['-c', 'import smart_memory; print(smart_memory.__version__)'],
            { encoding: 'utf8', stdio: 'pipe' }
        );

        return result.status === 0;
    } catch (e) {
        return false;
    }
}

// Install smart_memory via pip
function installSmartMemory(pythonCmd) {
    console.error('Installing smart_memory...');

    const install = spawn(pythonCmd, ['-m', 'pip', 'install', 'smart-memory'], {
        stdio: 'inherit'
    });

    return new Promise((resolve, reject) => {
        install.on('close', (code) => {
            if (code === 0) {
                resolve();
            } else {
                reject(new Error(`Installation failed with code ${code}`));
            }
        });
    });
}

// Main
async function main() {
    const python = findPython();

    if (!python) {
        console.error('Error: Python 3.11+ is required but not found.');
        console.error('Please install Python 3.11 or later: https://www.python.org/downloads/');
        process.exit(1);
    }

    // Check if smart_memory is installed
    if (!checkSmartMemoryInstalled(python)) {
        console.error('smart_memory package not found. Installing...');
        try {
            await installSmartMemory(python);
        } catch (e) {
            console.error('Failed to install smart_memory:', e.message);
            console.error('\nManual installation:');
            console.error(`  ${python} -m pip install smart-memory`);
            process.exit(1);
        }
    }

    // Launch the server
    const server = spawn(python, ['-m', 'smart_memory.server'], {
        stdio: 'inherit'
    });

    server.on('close', (code) => {
        process.exit(code || 0);
    });

    // Handle signals
    process.on('SIGINT', () => {
        server.kill('SIGINT');
    });

    process.on('SIGTERM', () => {
        server.kill('SIGTERM');
    });
}

main().catch((error) => {
    console.error('Error:', error.message);
    process.exit(1);
});
