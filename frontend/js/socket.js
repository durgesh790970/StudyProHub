// frontend/js/socket.js
// WebSocket client for real-time updates

class SocketClient {
    constructor(url = 'http://localhost:3000') {
        this.url = url;
        this.socket = null;
        this.connected = false;
        this.listeners = {};
        this.isClosed = false;
    }

    connect(token = null) {
        if (this.socket) return this.socket;

        try {
            // Load Socket.io from CDN if not installed
            if (typeof io === 'undefined') {
                console.warn('[Socket] Socket.io library not loaded. Using polling fallback.');
                return null;
            }

            const auth = token ? { token } : {};
            
            this.socket = io(this.url, {
                auth,
                reconnection: true,
                reconnectionDelay: 1000,
                reconnectionDelayMax: 5000,
                reconnectionAttempts: 5,
                transports: ['websocket', 'polling']
            });

            this.setupDefaultListeners();
            return this.socket;
        } catch (error) {
            console.error('[Socket] Connection failed:', error);
            return null;
        }
    }

    setupDefaultListeners() {
        this.socket.on('connect', () => {
            this.connected = true;
            console.log('[Socket] Connected:', this.socket.id);
            this.emit('connected');
        });

        this.socket.on('disconnect', () => {
            this.connected = false;
            console.log('[Socket] Disconnected');
            this.emit('disconnected');
        });

        this.socket.on('error', (error) => {
            console.error('[Socket] Error:', error);
            this.emit('error', error);
        });
    }

    on(event, callback) {
        if (!this.listeners[event]) {
            this.listeners[event] = [];
        }
        this.listeners[event].push(callback);

        if (this.socket) {
            this.socket.on(event, callback);
        }
    }

    off(event, callback) {
        if (this.listeners[event]) {
            this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
        }

        if (this.socket) {
            this.socket.off(event, callback);
        }
    }

    emit(event, data = null) {
        if (this.listeners[event]) {
            this.listeners[event].forEach(callback => callback(data));
        }

        if (this.socket && this.connected) {
            this.socket.emit(event, data);
        }
    }

    // ============================================
    // USER PRESENCE
    // ============================================

    userOnline(userId) {
        this.emit('userOnline', userId);
    }

    userOffline(userId) {
        this.emit('userOffline', userId);
    }

    onUserStatusChanged(callback) {
        this.on('userStatusChanged', callback);
    }

    // ============================================
    // CONTEST PARTICIPATION
    // ============================================

    joinContest(contestId, userId, username) {
        if (!this.socket || !this.connected) {
            console.warn('[Socket] Not connected. Cannot join contest.');
            return;
        }

        this.emit('joinContest', { contestId, userId, username });
    }

    leaveContest(contestId, userId, username) {
        this.emit('leaveContest', { contestId, userId, username });
    }

    onParticipantJoined(callback) {
        this.on('participantJoined', callback);
    }

    onParticipantLeft(callback) {
        this.on('participantLeft', callback);
    }

    // ============================================
    // LIVE SUBMISSIONS
    // ============================================

    submitCode(contestId, submissionId, userId, username, problemId, verdict) {
        this.emit('submissionCreated', {
            contestId,
            submissionId,
            userId,
            username,
            problemId,
            verdict
        });
    }

    updateSubmissionVerdict(contestId, submissionId, verdict, testResults) {
        this.emit('submissionUpdated', {
            contestId,
            submissionId,
            verdict,
            testResults
        });
    }

    onLiveSubmission(callback) {
        this.on('liveSubmission', callback);
    }

    onSubmissionVerdictUpdated(callback) {
        this.on('submissionVerdictUpdated', callback);
    }

    onSubmissionHistory(callback) {
        this.on('submissionHistory', callback);
    }

    // ============================================
    // LIVE LEADERBOARD
    // ============================================

    subscribeLeaderboard(contestId) {
        this.emit('subscribeLeaderboard', { contestId });
    }

    unsubscribeLeaderboard(contestId) {
        this.emit('unsubscribeLeaderboard', { contestId });
    }

    onLeaderboardUpdated(callback) {
        this.on('leaderboardUpdated', callback);
    }

    // ============================================
    // CONTEST COUNTDOWN TIMER
    // ============================================

    subscribeContestTimer(contestId, endTime) {
        this.emit('subscribeContestTimer', { contestId, endTime });
    }

    unsubscribeContestTimer(contestId) {
        this.emit('unsubscribeContestTimer', { contestId });
    }

    onTimerSync(callback) {
        this.on('timerSync', callback);
    }

    // ============================================
    // NOTIFICATIONS
    // ============================================

    sendNotification(userId, title, body, type = 'info', icon = '') {
        this.emit('sendNotification', { userId, title, body, type, icon });
    }

    onNotification(callback) {
        this.on('notification', callback);
    }

    // ============================================
    // CHAT
    // ============================================

    sendChatMessage(contestId, userId, username, message) {
        this.emit('contestChat', { contestId, userId, username, message });
    }

    onChatMessage(callback) {
        this.on('chatMessage', callback);
    }

    // ============================================
    // CONNECTION STATUS
    // ============================================

    isConnected() {
        return this.connected && this.socket && this.socket.connected;
    }

    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
            this.connected = false;
        }
    }
}

// Global instance
let socketClient = null;

function getSocket(token = null) {
    if (!socketClient) {
        socketClient = new SocketClient();
    }

    if (!socketClient.isConnected()) {
        socketClient.connect(token || localStorage.getItem('token'));
    }

    return socketClient;
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { SocketClient, getSocket };
}
