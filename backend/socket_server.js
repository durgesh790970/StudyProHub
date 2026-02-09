const io = require('socket.io')(3000, {
  cors: { origin: '*' }
});

console.log('Socket.IO server listening on :3000');

io.on('connection', (socket) => {
  console.log('client connected', socket.id);

  socket.on('join', (data) => {
    // Join a room named by user id
    const userId = data && data.userId;
    if (userId) {
      socket.join(String(userId));
      console.log(`socket ${socket.id} joined room ${userId}`);
    }
  });

  // server_emit is used by backend emitters to request server forward to a room
  socket.on('server_emit', (data) => {
    try {
      const to = data.to;
      const event = data.event;
      const payload = data.payload;
      if (to && event) {
        io.to(String(to)).emit(event, payload);
        console.log(`forwarded event ${event} to ${to}`);
      }
    } catch (e) {
      console.error('server_emit error', e);
    }
  });

  socket.on('disconnect', () => {
    console.log('client disconnected', socket.id);
  });
});