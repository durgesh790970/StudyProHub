/**
 * Database API Client - JavaScript utilities for frontend-backend communication
 * Handles all API calls to the backend database system
 */

class DatabaseAPIClient {
    constructor(baseURL = '') {
        this.baseURL = baseURL || window.location.origin;
        this.timeout = 30000; // 30 seconds
    }

    /**
     * Generic fetch wrapper with error handling
     */
    async fetch(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const defaultOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            },
            timeout: this.timeout
        };

        const finalOptions = { ...defaultOptions, ...options };

        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), this.timeout);

            const response = await fetch(url, {
                ...finalOptions,
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            // Parse response
            const data = await response.json().catch(() => ({}));

            // Handle API errors
            if (!response.ok) {
                throw {
                    status: response.status,
                    message: data.error || data.message || 'API Error',
                    data: data
                };
            }

            return {
                success: true,
                status: response.status,
                data: data
            };
        } catch (error) {
            if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
                return {
                    success: false,
                    error: 'Network error. Please check your connection.',
                    originalError: error
                };
            }

            // Handle both thrown objects and Error objects
            const errorMessage = error?.message || error?.error || 'Unknown error occurred';
            const errorStatus = error?.status || 0;

            return {
                success: false,
                error: errorMessage,
                status: errorStatus,
                originalError: error
            };
        }
    }

    /**
     * Register new user
     * POST /api/register/
     */
    async register(userData) {
        return this.fetch('/api/register/', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    }

    /**
     * Login user
     * POST /api/login/
     */
    async login(email, password) {
        return this.fetch('/api/login/', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
    }

    /**
     * Get user profile
     * GET /api/profile/<user_id>/
     */
    async getProfile(userId) {
        return this.fetch(`/api/profile/${userId}/`);
    }

    /**
     * Create user profile
     * POST /api/profile/<user_id>/
     */
    async createProfile(userId, profileData) {
        return this.fetch(`/api/profile/${userId}/`, {
            method: 'POST',
            body: JSON.stringify(profileData)
        });
    }

    /**
     * Update user profile
     * PUT /api/profile/<user_id>/
     */
    async updateProfile(userId, profileData) {
        return this.fetch(`/api/profile/${userId}/`, {
            method: 'PUT',
            body: JSON.stringify(profileData)
        });
    }

    /**
     * Get user transactions
     * GET /api/transactions/<user_id>/
     */
    async getTransactions(userId) {
        return this.fetch(`/api/transactions/${userId}/`);
    }

    /**
     * Create transaction
     * POST /api/transactions/<user_id>/
     */
    async createTransaction(userId, transactionData) {
        return this.fetch(`/api/transactions/${userId}/`, {
            method: 'POST',
            body: JSON.stringify(transactionData)
        });
    }

    /**
     * Get user test results
     * GET /api/test-results/<user_id>/
     */
    async getTestResults(userId) {
        return this.fetch(`/api/test-results/${userId}/`);
    }

    /**
     * Save test result
     * POST /api/test-results/<user_id>/
     */
    async saveTestResult(userId, testData) {
        return this.fetch(`/api/test-results/${userId}/`, {
            method: 'POST',
            body: JSON.stringify(testData)
        });
    }

    /**
     * Get complete user information
     * GET /api/user-info/<user_id>/
     */
    async getUserInfo(userId) {
        return this.fetch(`/api/user-info/${userId}/`);
    }

    /**
     * Get database statistics
     * GET /api/stats/
     */
    async getStats() {
        return this.fetch('/api/stats/');
    }

    /**
     * Track user activity
     * POST /api/track-activity/
     */
    async trackActivity(userId, activityType, title = '', description = '', data = {}) {
        return this.fetch('/api/track-activity/', {
            method: 'POST',
            body: JSON.stringify({
                userId,
                activityType,
                title,
                description,
                data
            })
        });
    }

    /**
     * Record PDF purchase
     * POST /api/purchases/pdf/
     */
    async recordPdfPurchase(userId, pdfId, pdfTitle, company, amount, transactionId = '') {
        return this.fetch('/api/purchases/pdf/', {
            method: 'POST',
            body: JSON.stringify({
                userId,
                pdfId,
                pdfTitle,
                company,
                amount,
                transactionId
            })
        });
    }

    /**
     * Record mock test attempt
     * POST /api/attempts/mock/
     */
    async recordMockAttempt(userId, mockId, mockTitle, score, totalQuestions, correctAnswers, duration = 0) {
        return this.fetch('/api/attempts/mock/', {
            method: 'POST',
            body: JSON.stringify({
                userId,
                mockId,
                mockTitle,
                score,
                totalQuestions,
                correctAnswers,
                duration,
                timestamp: new Date().toISOString()
            })
        });
    }

    /**
     * Record quiz/interview attempt
     * POST /api/attempts/quiz/
     */
    async recordQuizAttempt(userId, quizId, quizTitle, quizType, score, totalQuestions, correctAnswers) {
        return this.fetch('/api/attempts/quiz/', {
            method: 'POST',
            body: JSON.stringify({
                userId,
                quizId,
                quizTitle,
                quizType,
                score,
                totalQuestions,
                correctAnswers,
                timestamp: new Date().toISOString()
            })
        });
    }

    /**
     * Get complete user profile with all activities
     * GET /api/user-complete-profile/<user_id>/
     */
    async getUserCompleteProfile(userId) {
        return this.fetch(`/api/user-complete-profile/${userId}/`);
    }
}

/**
 * Form Handler - Manages form submissions to API endpoints
 */
class FormHandler {
    constructor(apiClient) {
        this.api = apiClient;
    }

    /**
     * Handle signup form submission
     */
    async handleSignup(formData) {
        // Validate form data
        const validation = this.validateSignupForm(formData);
        if (!validation.valid) {
            return {
                success: false,
                error: validation.error
            };
        }

        try {
            const response = await this.api.register(formData);

            if (response.success) {
                // Store user ID in localStorage
                localStorage.setItem('userId', response.data.user_id);
                localStorage.setItem('userEmail', response.data.email);
                
                return {
                    success: true,
                    message: response.data.message,
                    userId: response.data.user_id
                };
            } else {
                return {
                    success: false,
                    error: response.data?.error || response.error || 'Registration failed'
                };
            }
        } catch (error) {
            return {
                success: false,
                error: 'Registration failed: ' + (error.message || 'Unknown error')
            };
        }
    }

    /**
     * Handle login form submission
     */
    async handleLogin(email, password) {
        // Validate inputs
        if (!email || !password) {
            return {
                success: false,
                error: 'Email and password are required'
            };
        }

        try {
            const response = await this.api.login(email, password);

            // Check if response is successful
            if (response.success && response.data && response.data.user) {
                // Store user info
                const user = response.data.user;
                localStorage.setItem('userId', user.id);
                localStorage.setItem('userEmail', user.email);
                localStorage.setItem('userName', user.first_name || user.email);
                
                return {
                    success: true,
                    message: response.data.message || 'Login successful',
                    user: user
                };
            } else {
                // Get error message from multiple possible locations
                const errorMsg = response.data?.error || response.error || response.message || 'Login failed';
                return {
                    success: false,
                    error: String(errorMsg)
                };
            }
        } catch (error) {
            const errorMsg = error?.message || error?.error || 'Login failed';
            return {
                success: false,
                error: 'Login failed: ' + String(errorMsg)
            };
        }
    }

    /**
     * Handle profile update
     */
    async handleProfileUpdate(userId, profileData) {
        try {
            const response = await this.api.updateProfile(userId, profileData);

            if (response.success && response.data) {
                return {
                    success: true,
                    message: response.data.message || 'Profile updated successfully',
                    profile: response.data.profile
                };
            } else {
                const errorMsg = response.data?.error || response.error || response.message || 'Profile update failed';
                return {
                    success: false,
                    error: String(errorMsg)
                };
            }
        } catch (error) {
            const errorMsg = error?.message || error?.error || 'Profile update failed';
            return {
                success: false,
                error: 'Profile update failed: ' + String(errorMsg)
            };
        }
    }

    /**
     * Validate signup form
     */
    validateSignupForm(data) {
        if (!data.email) {
            return { valid: false, error: 'Email is required' };
        }
        if (!this.isValidEmail(data.email)) {
            return { valid: false, error: 'Invalid email format' };
        }
        if (!data.username) {
            return { valid: false, error: 'Username is required' };
        }
        if (!data.password) {
            return { valid: false, error: 'Password is required' };
        }
        if (data.password.length < 8) {
            return { valid: false, error: 'Password must be at least 8 characters' };
        }
        if (!data.first_name) {
            return { valid: false, error: 'First name is required' };
        }
        return { valid: true };
    }

    /**
     * Validate email format
     */
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
}

/**
 * DOM Event Handlers - Wire up forms and buttons to API calls
 */
class EventManager {
    constructor(apiClient, formHandler) {
        this.api = apiClient;
        this.formHandler = formHandler;
    }

    /**
     * Setup signup form event listeners
     */
    setupSignupForm(formSelector) {
        const form = document.querySelector(formSelector);
        if (!form) return;

        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            // Show loading state
            this.showLoading(form);

            // Get form data
            const formData = new FormData(form);
            const data = {
                email: formData.get('email'),
                username: formData.get('username'),
                password: formData.get('password'),
                first_name: formData.get('first_name'),
                last_name: formData.get('last_name') || '',
                phone: formData.get('phone') || ''
            };

            // Submit
            const result = await this.formHandler.handleSignup(data);
            
            this.hideLoading(form);

            if (result.success) {
                // Show success message
                this.showMessage(form, result.message, 'success');
                
                // Redirect after 2 seconds
                setTimeout(() => {
                    window.location.href = '/dashboard/';
                }, 2000);
            } else {
                this.showMessage(form, result.error, 'error');
            }
        });
    }

    /**
     * Setup login form event listeners
     */
    setupLoginForm(formSelector) {
        const form = document.querySelector(formSelector);
        if (!form) return;

        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            this.showLoading(form);

            const email = form.querySelector('[name="email"]').value;
            const password = form.querySelector('[name="password"]').value;

            const result = await this.formHandler.handleLogin(email, password);
            
            this.hideLoading(form);

            if (result.success) {
                this.showMessage(form, result.message, 'success');
                
                setTimeout(() => {
                    window.location.href = '/dashboard/';
                }, 1500);
            } else {
                this.showMessage(form, result.error, 'error');
            }
        });
    }

    /**
     * Setup profile form event listeners
     */
    setupProfileForm(formSelector) {
        const form = document.querySelector(formSelector);
        if (!form) return;

        const userId = localStorage.getItem('userId');
        if (!userId) {
            this.showMessage(form, 'Please login first', 'error');
            return;
        }

        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            this.showLoading(form);

            const formData = new FormData(form);
            const data = Object.fromEntries(formData);

            const result = await this.formHandler.handleProfileUpdate(userId, data);
            
            this.hideLoading(form);

            if (result.success) {
                this.showMessage(form, result.message, 'success');
            } else {
                this.showMessage(form, result.error, 'error');
            }
        });
    }

    /**
     * Show loading state
     */
    showLoading(element) {
        const button = element.querySelector('button[type="submit"]');
        if (button) {
            button.disabled = true;
            button.textContent = 'Loading...';
        }
    }

    /**
     * Hide loading state
     */
    hideLoading(element) {
        const button = element.querySelector('button[type="submit"]');
        if (button) {
            button.disabled = false;
            button.textContent = button.getAttribute('data-original-text') || 'Submit';
        }
    }

    /**
     * Show message
     */
    showMessage(element, message, type = 'info') {
        let messageDiv = element.querySelector('.api-message');
        if (!messageDiv) {
            messageDiv = document.createElement('div');
            messageDiv.className = 'api-message';
            element.insertBefore(messageDiv, element.firstChild);
        }

        messageDiv.textContent = message;
        messageDiv.className = `api-message alert alert-${type === 'error' ? 'danger' : type}`;
        messageDiv.style.display = 'block';

        // Auto-hide after 5 seconds (except for errors)
        if (type !== 'error') {
            setTimeout(() => {
                messageDiv.style.display = 'none';
            }, 5000);
        }
    }
}

// ============================================================================
// Initialize API Client and Form Handlers
// ============================================================================

// Create global API client instance
const dbAPI = new DatabaseAPIClient();

// Create form handler
const formHandler = new FormHandler(dbAPI);

// Create event manager
const eventManager = new EventManager(dbAPI, formHandler);

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    // Setup forms if they exist
    eventManager.setupSignupForm('form[name="signup-form"]');
    eventManager.setupSignupForm('form[action="/signup/"]');
    
    eventManager.setupLoginForm('form[name="login-form"]');
    eventManager.setupLoginForm('form[action="/login/"]');
    
    eventManager.setupProfileForm('form[name="profile-form"]');
    eventManager.setupProfileForm('form[action="/profile/"]');
    
    console.log('Database API Client initialized');
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { DatabaseAPIClient, FormHandler, EventManager };
}
