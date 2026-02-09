/**
 * User Activity Tracker
 * Helper module to easily track user activities across the application
 */

class ActivityTracker {
    constructor(apiClient) {
        this.api = apiClient;
        this.userId = this.getUserId();
    }

    /**
     * Get user ID from localStorage or session
     */
    getUserId() {
        return localStorage.getItem('userId') || sessionStorage.getItem('userId');
    }

    /**
     * Track login activity
     */
    async trackLogin() {
        if (!this.userId) return;
        return await this.api.trackActivity(
            this.userId,
            'login',
            'User Logged In',
            'User successfully logged in to the platform'
        );
    }

    /**
     * Track logout activity
     */
    async trackLogout() {
        if (!this.userId) return;
        return await this.api.trackActivity(
            this.userId,
            'logout',
            'User Logged Out',
            'User logged out from the platform'
        );
    }

    /**
     * Track PDF purchase
     */
    async trackPdfPurchase(pdfData) {
        if (!this.userId) return;
        return await this.api.recordPdfPurchase(
            this.userId,
            pdfData.pdfId || 0,
            pdfData.title,
            pdfData.company || 'Unknown',
            pdfData.amount || 0,
            pdfData.transactionId || ''
        );
    }

    /**
     * Track PDF view
     */
    async trackPdfView(pdfTitle, company) {
        if (!this.userId) return;
        return await this.api.trackActivity(
            this.userId,
            'pdf_view',
            `Viewed: ${pdfTitle}`,
            `Viewed PDF from ${company}`
        );
    }

    /**
     * Track mock test attempt
     */
    async trackMockAttempt(mockData) {
        if (!this.userId) return;
        return await this.api.recordMockAttempt(
            this.userId,
            mockData.mockId || 0,
            mockData.title,
            mockData.score,
            mockData.totalQuestions,
            mockData.correctAnswers,
            mockData.duration || 0
        );
    }

    /**
     * Track quiz/interview attempt
     */
    async trackQuizAttempt(quizData) {
        if (!this.userId) return;
        return await this.api.recordQuizAttempt(
            this.userId,
            quizData.quizId,
            quizData.title,
            quizData.type || 'technical',
            quizData.score,
            quizData.totalQuestions,
            quizData.correctAnswers
        );
    }

    /**
     * Track generic activity
     */
    async trackActivity(activityType, title, description = '', data = {}) {
        if (!this.userId) return;
        return await this.api.trackActivity(
            this.userId,
            activityType,
            title,
            description,
            data
        );
    }

    /**
     * Get user's complete profile with all activities
     */
    async getUserProfile() {
        if (!this.userId) return null;
        return await this.api.getUserCompleteProfile(this.userId);
    }

    /**
     * Get user's recent activities
     */
    async getUserActivities(limit = 20) {
        const profile = await this.getUserProfile();
        if (!profile?.success || !profile.profile?.activities) {
            return [];
        }
        return profile.profile.activities.slice(0, limit);
    }

    /**
     * Get user's purchases
     */
    async getUserPurchases() {
        const profile = await this.getUserProfile();
        if (!profile?.success || !profile.profile?.purchases) {
            return [];
        }
        return profile.profile.purchases;
    }

    /**
     * Get user's mock test attempts
     */
    async getUserMockAttempts() {
        const profile = await this.getUserProfile();
        if (!profile?.success || !profile.profile?.mockAttempts) {
            return [];
        }
        return profile.profile.mockAttempts;
    }

    /**
     * Get user statistics
     */
    async getUserStatistics() {
        const profile = await this.getUserProfile();
        if (!profile?.success || !profile.profile?.statistics) {
            return null;
        }
        return profile.profile.statistics;
    }
}

// Initialize activity tracker when page loads
document.addEventListener('DOMContentLoaded', () => {
    // Make activity tracker available globally
    if (typeof dbAPI !== 'undefined') {
        window.activityTracker = new ActivityTracker(dbAPI);
        console.log('✓ Activity Tracker initialized');
    }
});

// Track user login when they log in
if (window.location.pathname.includes('/login')) {
    document.addEventListener('DOMContentLoaded', () => {
        // Listen for successful login
        const originalFetch = window.fetch;
        window.fetch = async (...args) => {
            const response = await originalFetch(...args);
            
            // If login API call succeeds, track it
            if (args[0].includes('/api/login/') && response.status === 200) {
                setTimeout(async () => {
                    if (window.activityTracker) {
                        await window.activityTracker.trackLogin();
                    }
                }, 500);
            }
            
            return response;
        };
    });
}

// Track logout
function trackUserLogout() {
    if (window.activityTracker) {
        window.activityTracker.trackLogout(); 
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ActivityTracker;
}
