// backend/socketConfig.js
// Socket.io configuration middleware

const socketIO = require('socket.io');

const initializeSocket = (server) => {
    const io = socketIO(server, {
        cors: {
            origin: process.env.FRONTEND_URL || 'http://localhost:3001',
            credentials: true
        },
        transports: ['websocket', 'polling'],
        reconnection: true,
        reconnectionDelay: 1000,
        reconnectionDelayMax: 5000,
        reconnectionAttempts: 5
    });

    // Middleware for authentication
    io.use((socket, next) => {
        const token = socket.handshake.auth.token;
        
        if (token) {
            try {
                // Verify JWT token
                const jwt = require('jsonwebtoken');
                const decoded = jwt.verify(token, process.env.JWT_SECRET);
                socket.userId = decoded.userId;
                socket.userRole = decoded.role || 'user';
                next();
            } catch (error) {
                console.error('[Socket] Authentication error:', error.message);
                next(new Error('Authentication failed'));
            }
        } else {
            // Allow unauthenticated connections for public features
            next();
        }
    });

    // Load socket handlers
    const socketHandler = require('./socket/socketHandler');
    socketHandler(io);

    return io;
};

module.exports = initializeSocket;
