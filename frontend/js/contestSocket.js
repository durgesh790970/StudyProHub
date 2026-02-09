// frontend/js/contestSocket.js
// Contest-specific WebSocket utilities

class ContestSocketManager {
    constructor(contestId, token = null) {
        this.contestId = contestId;
        this.token = token || localStorage.getItem('token');
        this.socket = getSocket(this.token);
        this.leaderboard = [];
        this.submissions = [];
        this.participants = 0;
        this.timeRemaining = 0;
        this.timerInterval = null;
        this.callbacksLeaderboard = [];
        this.callbacksSubmission = [];
        this.callbacksTimer = [];
    }

    init() {
        if (!this.socket || !this.socket.isConnected()) {
            console.warn('[Contest] Socket not connected');
            return;
        }

        // Join contest
        const userProfile = JSON.parse(localStorage.getItem('userProfile') || '{}');
        if (userProfile._id && userProfile.username) {
            this.socket.joinContest(
                this.contestId, 
                userProfile._id, 
                userProfile.username
            );
        }

        // Subscribe to updates
        this.socket.subscribeLeaderboard(this.contestId);
        this.socket.subscribeContestTimer(this.contestId, this.getContestEndTime());

        // Setup listeners
        this.setupListeners();
    }

    setupListeners() {
        // Participant updates
        this.socket.onParticipantJoined((data) => {
            this.participants = data.totalParticipants;
            console.log(`[Contest] ${data.username} joined (${data.totalParticipants} total)`);
            this.notifyCallbacks('participant', data);
        });

        this.socket.onParticipantLeft((data) => {
            this.participants = data.totalParticipants;
            console.log(`[Contest] ${data.username} left (${data.totalParticipants} total)`);
            this.notifyCallbacks('participant', data);
        });

        // Submission updates
        this.socket.onLiveSubmission((data) => {
            this.submissions.push(data);
            console.log(`[Contest] ${data.username} submitted: ${data.verdict}`);
            this.notifyCallbacks('submission', data);
        });

        this.socket.onSubmissionVerdictUpdated((data) => {
            const submission = this.submissions.find(s => s.submissionId === data.submissionId);
            if (submission) {
                submission.verdict = data.verdict;
                submission.testResults = data.testResults;
            }
            console.log(`[Contest] Submission ${data.submissionId} updated: ${data.verdict}`);
            this.notifyCallbacks('submissionUpdate', data);
        });

        // Leaderboard updates
        this.socket.onLeaderboardUpdated((data) => {
            this.leaderboard = data.leaderboard;
            console.log('[Contest] Leaderboard updated');
            this.notifyCallbacks('leaderboard', data);
        });

        // Timer sync
        this.socket.onTimerSync((data) => {
            this.timeRemaining = data.timeRemaining;
            this.startCountdown();
        });

        // Chat messages
        this.socket.onChatMessage((data) => {
            console.log(`[Contest Chat] ${data.username}: ${data.message}`);
            this.notifyCallbacks('chat', data);
        });

        // Submissions history
        this.socket.onSubmissionHistory((data) => {
            this.submissions = data.submissions;
            console.log(`[Contest] Loaded ${data.submissions.length} submissions`);
        });
    }

    startCountdown() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
        }

        this.timerInterval = setInterval(() => {
            this.timeRemaining = Math.max(0, this.timeRemaining - 1000);
            this.notifyCallbacks('timer', { timeRemaining: this.timeRemaining });

            if (this.timeRemaining <= 0) {
                clearInterval(this.timerInterval);
                this.notifyCallbacks('contestEnded', { message: 'Contest has ended' });
            }
        }, 1000);
    }

    getContestEndTime() {
        // Get from page/data
        return document.querySelector('[data-end-time]')?.dataset.endTime || new Date();
    }

    onLeaderboardUpdate(callback) {
        this.callbacksLeaderboard.push(callback);
    }

    onSubmissionUpdate(callback) {
        this.callbacksSubmission.push(callback);
    }

    onTimerUpdate(callback) {
        this.callbacksTimer.push(callback);
    }

    notifyCallbacks(type, data) {
        if (type === 'leaderboard') {
            this.callbacksLeaderboard.forEach(cb => cb(data));
        } else if (type === 'submission' || type === 'submissionUpdate') {
            this.callbacksSubmission.forEach(cb => cb(data));
        } else if (type === 'timer') {
            this.callbacksTimer.forEach(cb => cb(data));
        }
    }

    submitSolution(submissionId, problemId, verdict) {
        const userProfile = JSON.parse(localStorage.getItem('userProfile') || '{}');
        this.socket.submitCode(
            this.contestId,
            submissionId,
            userProfile._id,
            userProfile.username,
            problemId,
            verdict
        );
    }

    sendMessage(message) {
        const userProfile = JSON.parse(localStorage.getItem('userProfile') || '{}');
        this.socket.sendChatMessage(
            this.contestId,
            userProfile._id,
            userProfile.username,
            message
        );
    }

    getLeaderboard() {
        return this.leaderboard;
    }

    getSubmissions() {
        return this.submissions;
    }

    getTimeRemaining() {
        return this.timeRemaining;
    }

    getParticipantCount() {
        return this.participants;
    }

    formatTime(milliseconds) {
        const totalSeconds = Math.floor(milliseconds / 1000);
        const hours = Math.floor(totalSeconds / 3600);
        const minutes = Math.floor((totalSeconds % 3600) / 60);
        const seconds = totalSeconds % 60;

        if (hours > 0) {
            return `${hours}h ${minutes}m ${seconds}s`;
        }
        return `${minutes}m ${seconds}s`;
    }

    disconnect() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
        }

        const userProfile = JSON.parse(localStorage.getItem('userProfile') || '{}');
        if (userProfile._id && userProfile.username) {
            this.socket.leaveContest(
                this.contestId,
                userProfile._id,
                userProfile.username
            );
        }

        this.socket.unsubscribeLeaderboard(this.contestId);
        this.socket.unsubscribeContestTimer(this.contestId);
    }
}

// Export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ContestSocketManager };
}
