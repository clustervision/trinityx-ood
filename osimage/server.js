const express = require('express');
const http = require('http');
const socketio = require('socket.io');
const { spawn } = require('child_process');
const os = require('os');

const app = express();
const server = http.createServer(app);
const io = socketio(server);

app.use(express.static(__dirname));

// Function to get the current prompt (user and directory)
function getPrompt() {
    const user = os.userInfo().username;  // Get current user
    return new Promise((resolve, reject) => {
        const shellPrompt = spawn('bash', ['-c', 'pwd']);  // Run pwd in a separate bash process
        shellPrompt.stdout.on('data', (data) => {
            const currentDir = data.toString().trim();  // Get current directory
            const prompt = `[${user}@${os.hostname()} ${currentDir}]# `;  // Format the prompt
            resolve(prompt);
        });
    });
}

io.on('connection', async (socket) => {
    console.log('New client connected');

    const shell = spawn('bash');  // Spawns a bash shell process

    // Send initial prompt when user connects
    const prompt = await getPrompt();
    socket.emit('output', prompt);

    shell.stdout.on('data', (data) => {
        const formattedData = data.toString().replace(/\n/g, '\r\n');  // Ensure proper newlines
        console.log("Shell stdout:", formattedData);
        socket.emit('output', formattedData);  // Send command output to client
    });

    shell.stderr.on('data', (data) => {
        const formattedData = data.toString().replace(/\n/g, '\r\n');  // Ensure proper newlines
        console.log("Shell stderr:", formattedData);
        socket.emit('output', formattedData);  // Send error output to client
    });

    shell.on('close', (code) => {
        console.log("Shell exited with code:", code);
        socket.emit('output', `Shell exited with code: ${code}\r\n`);
    });

    socket.on('command', async (cmd) => {
        console.log("Received command: ", cmd);
        shell.stdin.write(cmd);  // Write the command to the shell

        shell.stdout.once('data', async (data) => {
            // After processing the command, send a new prompt
            const prompt = await getPrompt();
            socket.emit('output', prompt);
        });
    });

    socket.on('disconnect', () => {
        console.log('Client disconnected');
    });
});

server.listen(3000, () => {
    console.log('Server running on http://localhost:3000');
});
