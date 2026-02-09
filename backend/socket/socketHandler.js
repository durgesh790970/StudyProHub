// backend/socket/socketHandler.js
// WebSocket event handlers for real-time updates

const socketHandler = (io) => {
    const onlineUsers = new Map(); // userId -> socketId
    const activeContests = new Map(); // contestId -> { participants, submissions }

    io.on('connection', (socket) => {
        console.log(`[Socket] New connection: ${socket.id}`);

        // ============================================
        // USER PRESENCE
        // ============================================

        socket.on('userOnline', (userId) => {
            onlineUsers.set(userId, socket.id);
            socket.userId = userId;
            
            // Broadcast user status
            io.emit('userStatusChanged', {
                userId,
                status: 'online',
                timestamp: new Date()
            });

            console.log(`[Socket] User ${userId} online`);
        });

        socket.on('userOffline', (userId) => {
            onlineUsers.delete(userId);
            
            io.emit('userStatusChanged', {
                userId,
                status: 'offline',
                timestamp: new Date()
            });

            console.log(`[Socket] User ${userId} offline`);
        });

        // ============================================
        // CONTEST PARTICIPATION
        // ============================================

        socket.on('joinContest', ({ contestId, userId, username }) => {
            const contestRoom = `contest-${contestId}`;
            socket.join(contestRoom);

            if (!activeContests.has(contestId)) {
                activeContests.set(contestId, {
                    participants: new Set(),
                    submissions: [],
                    startTime: new Date()
                });
            }

            const contest = activeContests.get(contestId);
            contest.participants.add(userId);

            // Notify others in contest
            io.to(contestRoom).emit('participantJoined', {
                contestId,
                userId,
                username,
                totalParticipants: contest.participants.size,
                timestamp: new Date()
            });

            // Send current submission data to new participant
            socket.emit('submissionHistory', {
                submissions: contest.submissions
            });

            console.log(`[Socket] ${username} joined contest ${contestId}`);
        });

        socket.on('leaveContest', ({ contestId, userId, username }) => {
            const contestRoom = `contest-${contestId}`;
            socket.leave(contestRoom);

            const contest = activeContests.get(contestId);
            if (contest) {
                contest.participants.delete(userId);
                
                if (contest.participants.size === 0) {
                    activeContests.delete(contestId);
                }
            }

            io.to(contestRoom).emit('participantLeft', {
                contestId,
                userId,
                username,
                totalParticipants: contest?.participants.size || 0,
                timestamp: new Date()
            });

            console.log(`[Socket] ${username} left contest ${contestId}`);
        });

        // ============================================
        // LIVE SUBMISSIONS
        // ============================================

        socket.on('submissionCreated', ({ contestId, submissionId, userId, username, problemId, verdict }) => {
            const contestRoom = `contest-${contestId}`;
            const contest = activeContests.get(contestId);

            if (contest) {
                contest.submissions.push({
                    submissionId,
                    userId,
                    username,
                    problemId,
                    verdict,
                    timestamp: new Date()
                });
            }

            // Emit to all participants in contest
            io.to(contestRoom).emit('liveSubmission', {
                submissionId,
                userId,
                username,
                problemId,
                verdict,
                timestamp: new Date()
            });

            console.log(`[Socket] Submission ${submissionId} from ${username}: ${verdict}`);
        });

        socket.on('submissionUpdated', ({ contestId, submissionId, verdict, testResults }) => {
            const contestRoom = `contest-${contestId}`;

            io.to(contestRoom).emit('submissionVerdictUpdated', {
                submissionId,
                verdict,
                testResults,
                timestamp: new Date()
            });

            console.log(`[Socket] Submission ${submissionId} updated: ${verdict}`);
        });

        // ============================================
        // LIVE LEADERBOARD
        // ============================================

        socket.on('subscribeLeaderboard', ({ contestId }) => {
            const leaderboardRoom = `leaderboard-${contestId}`;
            socket.join(leaderboardRoom);
            console.log(`[Socket] User subscribed to leaderboard: ${contestId}`);
        });

        socket.on('unsubscribeLeaderboard', ({ contestId }) => {
            const leaderboardRoom = `leaderboard-${contestId}`;
            socket.leave(leaderboardRoom);
        });

        // Called when leaderboard is updated (from backend)
        socket.on('updateLeaderboard', ({ contestId, leaderboard }) => {
            const leaderboardRoom = `leaderboard-${contestId}`;
            
            io.to(leaderboardRoom).emit('leaderboardUpdated', {
                contestId,
                leaderboard,
                timestamp: new Date()
            });

            console.log(`[Socket] Leaderboard updated for contest ${contestId}`);
        });

        // ============================================
        // CONTEST COUNTDOWN
        // ============================================

        socket.on('subscribeContestTimer', ({ contestId, endTime }) => {
            const timerRoom = `timer-${contestId}`;
            socket.join(timerRoom);

            // Calculate time remaining
            const now = new Date();
            const end = new Date(endTime);
            const timeRemaining = Math.max(0, end - now);

            socket.emit('timerSync', {
                contestId,
                timeRemaining,
                endTime
            });

            console.log(`[Socket] User subscribed to contest timer: ${contestId}`);
        });

        socket.on('unsubscribeContestTimer', ({ contestId }) => {
            const timerRoom = `timer-${contestId}`;
            socket.leave(timerRoom);
        });

        // ============================================
        // NOTIFICATIONS
        // ============================================

        socket.on('sendNotification', ({ userId, title, body, type, icon }) => {
            const recipientSocketId = onlineUsers.get(userId);
            
            if (recipientSocketId) {
                io.to(recipientSocketId).emit('notification', {
                    title,
                    body,
                    type, // 'success', 'error', 'info', 'warning'
                    icon,
                    timestamp: new Date()
                });

                console.log(`[Socket] Notification sent to ${userId}`);
            }
        });

        // ============================================
        // CHAT (Optional - for live contests)
        // ============================================

        socket.on('contestChat', ({ contestId, userId, username, message }) => {
            const contestRoom = `contest-${contestId}`;

            // Filter for spam/profanity could be added here
            io.to(contestRoom).emit('chatMessage', {
                userId,
                username,
                message,
                timestamp: new Date()
            });

            console.log(`[Socket] Chat in contest ${contestId}: ${username}`);
        });

        // ============================================
        // DISCONNECT
        // ============================================

        socket.on('disconnect', () => {
            const userId = socket.userId;
            
            if (userId) {
                onlineUsers.delete(userId);
                
                io.emit('userStatusChanged', {
                    userId,
                    status: 'offline',
                    timestamp: new Date()
                });
            }

            // Clean up any contest rooms
            socket.rooms.forEach(room => {
                if (room.startsWith('contest-')) {
                    const contestId = room.replace('contest-', '');
                    const contest = activeContests.get(contestId);
                    if (contest) {
                        contest.participants.delete(userId);
                        if (contest.participants.size === 0) {
                            activeContests.delete(contestId);
                        }
                    }
                }
            });

            console.log(`[Socket] User disconnected: ${socket.id}`);
        });

        // ============================================
        // ERROR HANDLING
        // ============================================

        socket.on('error', (error) => {
            console.error(`[Socket] Error on ${socket.id}:`, error);
        });
    });

    return {
        getOnlineUsersCount: () => onlineUsers.size,
        getOnlineUsers: () => Array.from(onlineUsers.keys()),
        getActiveContestCount: () => activeContests.size,
        getContestInfo: (contestId) => activeContests.get(contestId)
    };
};

module.exports = socketHandler;
