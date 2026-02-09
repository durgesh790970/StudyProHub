// backend/jobs/jobQueue.js
// Background job queue using Bull and Redis

const Queue = require('bull');
const axios = require('axios');
const RedisCache = require('../cache/redisClient');

// Initialize queues
const submissionQueue = new Queue('submissions', {
    redis: {
        host: process.env.REDIS_HOST || 'localhost',
        port: process.env.REDIS_PORT || 6379
    }
});

const emailQueue = new Queue('emails', {
    redis: {
        host: process.env.REDIS_HOST || 'localhost',
        port: process.env.REDIS_PORT || 6379
    }
});

const reportQueue = new Queue('reports', {
    redis: {
        host: process.env.REDIS_HOST || 'localhost',
        port: process.env.REDIS_PORT || 6379
    }
});

const leaderboardQueue = new Queue('leaderboard', {
    redis: {
        host: process.env.REDIS_HOST || 'localhost',
        port: process.env.REDIS_PORT || 6379
    }
});

class JobManager {
    // Submission processing job
    static setupSubmissionQueue() {
        submissionQueue.process('process-submission', 5, async (job) => {
            const { submissionId, userId, problemId, code, language, contestId } = job.data;
            
            try {
                console.log(`[Job] Processing submission ${submissionId}`);

                // Call Judge0 API to execute code
                const result = await this.executeCodeWithJudge0(code, language, problemId);

                // Update submission status in database
                // This would typically call a database update function
                // await updateSubmissionVerdict(submissionId, result);

                // Invalidate leaderboard cache if in contest
                if (contestId) {
                    const cache = RedisCache.getInstance();
                    await cache.invalidateLeaderboard(contestId);
                }

                console.log(`[Job] Submission ${submissionId} processed successfully`);
                return result;

            } catch (error) {
                console.error(`[Job] Submission ${submissionId} failed:`, error.message);
                throw error;
            }
        });

        submissionQueue.on('failed', (job, err) => {
            console.error(`[Job] Submission job failed:`, err.message);
            // Could send failure notification here
        });

        submissionQueue.on('completed', (job) => {
            console.log(`[Job] Submission job completed`);
        });
    }

    // Email sending job
    static setupEmailQueue() {
        emailQueue.process('send-email', 10, async (job) => {
            const { to, subject, template, data } = job.data;

            try {
                console.log(`[Job] Sending email to ${to}`);

                // Email sending logic would go here
                // await sendEmail(to, subject, template, data);

                console.log(`[Job] Email sent to ${to}`);
                return { sent: true, to };

            } catch (error) {
                console.error(`[Job] Email to ${to} failed:`, error.message);
                throw error;
            }
        });

        emailQueue.on('failed', (job, err) => {
            console.error(`[Job] Email job failed:`, err.message);
        });
    }

    // Report generation job
    static setupReportQueue() {
        reportQueue.process('generate-report', 3, async (job) => {
            const { reportId, userId, type, filters } = job.data;

            try {
                console.log(`[Job] Generating ${type} report for user ${userId}`);

                // Generate report based on type
                const reportData = await this.generateReport(type, userId, filters);

                // Store report data
                // await saveReport(reportId, reportData);

                // Invalidate user cache
                const cache = RedisCache.getInstance();
                await cache.invalidateUserProfile(userId);

                console.log(`[Job] Report ${reportId} generated successfully`);
                return reportData;

            } catch (error) {
                console.error(`[Job] Report generation failed:`, error.message);
                throw error;
            }
        });

        reportQueue.on('failed', (job, err) => {
            console.error(`[Job] Report job failed:`, err.message);
        });
    }

    // Leaderboard update job
    static setupLeaderboardQueue() {
        leaderboardQueue.process('update-leaderboard', 5, async (job) => {
            const { contestId } = job.data;

            try {
                console.log(`[Job] Updating leaderboard for contest ${contestId}`);

                // Fetch all submissions for contest
                // const submissions = await getContestSubmissions(contestId);
                // Calculate rankings
                // const leaderboard = calculateRankings(submissions);

                // Cache updated leaderboard
                const cache = RedisCache.getInstance();
                // await cache.cacheLeaderboard(contestId, leaderboard, 300);

                console.log(`[Job] Leaderboard ${contestId} updated`);
                return { updated: true, contestId };

            } catch (error) {
                console.error(`[Job] Leaderboard update failed:`, error.message);
                throw error;
            }
        });

        leaderboardQueue.on('failed', (job, err) => {
            console.error(`[Job] Leaderboard job failed:`, err.message);
        });
    }

    // Helper: Execute code with Judge0
    static async executeCodeWithJudge0(code, language, problemId) {
        try {
            // Create submission on Judge0
            const createResponse = await axios.post(
                `${process.env.JUDGE0_API_URL || 'https://judge0-ce.p.rapidapi.com'}/submissions`,
                {
                    source_code: code,
                    language_id: this.getLanguageId(language),
                    stdin: '', // Test input would go here
                    expected_output: '' // Expected output would go here
                },
                {
                    headers: {
                        'X-RapidAPI-Key': process.env.JUDGE0_API_KEY,
                        'X-RapidAPI-Host': 'judge0-ce.p.rapidapi.com'
                    }
                }
            );

            const tokenId = createResponse.data.token;

            // Poll for result
            let result = null;
            const maxAttempts = 30;
            let attempts = 0;

            while (attempts < maxAttempts) {
                const getResponse = await axios.get(
                    `${process.env.JUDGE0_API_URL}/submissions/${tokenId}`,
                    {
                        headers: {
                            'X-RapidAPI-Key': process.env.JUDGE0_API_KEY,
                            'X-RapidAPI-Host': 'judge0-ce.p.rapidapi.com'
                        }
                    }
                );

                result = getResponse.data;

                // If status is completed, break
                if (result.status.id > 2) {
                    break;
                }

                // Wait before next poll
                await new Promise(resolve => setTimeout(resolve, 1000));
                attempts++;
            }

            return {
                verdict: this.getVerdictFromStatus(result.status.id),
                output: result.stdout || '',
                error: result.stderr || '',
                executionTime: result.time || 0,
                memory: result.memory || 0
            };

        } catch (error) {
            console.error('[Judge0] Execution error:', error.message);
            throw error;
        }
    }

    // Helper: Get language ID for Judge0
    static getLanguageId(language) {
        const languageMap = {
            'python': 71,
            'cpp': 54,
            'c': 50,
            'java': 62,
            'javascript': 63,
            'rust': 73,
            'go': 60
        };
        return languageMap[language.toLowerCase()] || 71; // Default to Python
    }

    // Helper: Get verdict from Judge0 status
    static getVerdictFromStatus(statusId) {
        const statusMap = {
            1: 'IN_QUEUE',
            2: 'PROCESSING',
            3: 'ACCEPTED',
            4: 'WRONG_ANSWER',
            5: 'TIME_LIMIT_EXCEEDED',
            6: 'COMPILATION_ERROR',
            7: 'RUNTIME_ERROR',
            8: 'INTERNAL_ERROR'
        };
        return statusMap[statusId] || 'UNKNOWN';
    }

    // Helper: Generate reports
    static async generateReport(type, userId, filters) {
        // Placeholder for report generation logic
        return {
            type,
            userId,
            generatedAt: new Date(),
            data: filters
        };
    }

    // Public methods to add jobs

    static async addSubmissionJob(submissionData) {
        return submissionQueue.add('process-submission', submissionData, {
            attempts: 3,
            backoff: {
                type: 'exponential',
                delay: 2000
            },
            removeOnComplete: true
        });
    }

    static async addEmailJob(emailData) {
        return emailQueue.add('send-email', emailData, {
            attempts: 3,
            backoff: {
                type: 'exponential',
                delay: 5000
            },
            removeOnComplete: true
        });
    }

    static async addReportJob(reportData) {
        return reportQueue.add('generate-report', reportData, {
            attempts: 2,
            backoff: {
                type: 'fixed',
                delay: 10000
            }
        });
    }

    static async addLeaderboardJob(contestId) {
        return leaderboardQueue.add('update-leaderboard', { contestId }, {
            priority: 10, // Higher priority
            removeOnComplete: true
        });
    }

    // Queue management

    static async getQueueStats() {
        return {
            submissions: {
                active: await submissionQueue.getActiveCount(),
                waiting: await submissionQueue.getWaitingCount(),
                completed: await submissionQueue.getCompletedCount(),
                failed: await submissionQueue.getFailedCount()
            },
            emails: {
                active: await emailQueue.getActiveCount(),
                waiting: await emailQueue.getWaitingCount(),
                completed: await emailQueue.getCompletedCount(),
                failed: await emailQueue.getFailedCount()
            },
            reports: {
                active: await reportQueue.getActiveCount(),
                waiting: await reportQueue.getWaitingCount(),
                completed: await reportQueue.getCompletedCount(),
                failed: await reportQueue.getFailedCount()
            },
            leaderboard: {
                active: await leaderboardQueue.getActiveCount(),
                waiting: await leaderboardQueue.getWaitingCount(),
                completed: await leaderboardQueue.getCompletedCount(),
                failed: await leaderboardQueue.getFailedCount()
            }
        };
    }

    static async clearCompletedJobs() {
        await submissionQueue.clean(1000, 'completed');
        await emailQueue.clean(1000, 'completed');
        await reportQueue.clean(1000, 'completed');
        await leaderboardQueue.clean(1000, 'completed');
    }

    static async closeQueues() {
        await submissionQueue.close();
        await emailQueue.close();
        await reportQueue.close();
        await leaderboardQueue.close();
    }
}

module.exports = JobManager;
