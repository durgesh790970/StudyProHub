// backend/cache/redisClient.js
// Redis cache initialization and utilities

const redis = require('redis');

class RedisCache {
    constructor(url = process.env.REDIS_URL || 'redis://localhost:6379') {
        this.client = redis.createClient({ url });
        this.isConnected = false;
        this.defaultTTL = 3600; // 1 hour default
    }

    async connect() {
        try {
            this.client.on('error', (err) => console.error('[Redis] Error:', err));
            this.client.on('connect', () => console.log('[Redis] Connected'));
            
            await this.client.connect();
            this.isConnected = true;
            console.log('[Redis] Cache initialized');
        } catch (error) {
            console.error('[Redis] Connection failed:', error);
            throw error;
        }
    }

    async disconnect() {
        if (this.isConnected) {
            await this.client.quit();
            this.isConnected = false;
        }
    }

    // ============================================
    // BASIC OPERATIONS
    // ============================================

    async set(key, value, ttl = this.defaultTTL) {
        try {
            const serialized = JSON.stringify(value);
            if (ttl) {
                await this.client.setEx(key, ttl, serialized);
            } else {
                await this.client.set(key, serialized);
            }
            console.log(`[Cache] SET: ${key}`);
            return true;
        } catch (error) {
            console.error(`[Cache] SET error for ${key}:`, error);
            return false;
        }
    }

    async get(key) {
        try {
            const data = await this.client.get(key);
            if (data) {
                console.log(`[Cache] HIT: ${key}`);
                return JSON.parse(data);
            }
            console.log(`[Cache] MISS: ${key}`);
            return null;
        } catch (error) {
            console.error(`[Cache] GET error for ${key}:`, error);
            return null;
        }
    }

    async delete(key) {
        try {
            await this.client.del(key);
            console.log(`[Cache] DELETE: ${key}`);
            return true;
        } catch (error) {
            console.error(`[Cache] DELETE error for ${key}:`, error);
            return false;
        }
    }

    async exists(key) {
        try {
            const exists = await this.client.exists(key);
            return exists === 1;
        } catch (error) {
            console.error(`[Cache] EXISTS error for ${key}:`, error);
            return false;
        }
    }

    async clear(pattern = '*') {
        try {
            const keys = await this.client.keys(pattern);
            if (keys.length > 0) {
                await this.client.del(keys);
                console.log(`[Cache] CLEARED: ${keys.length} keys matching ${pattern}`);
            }
            return true;
        } catch (error) {
            console.error(`[Cache] CLEAR error:`, error);
            return false;
        }
    }

    // ============================================
    // LEADERBOARD CACHING
    // ============================================

    async cacheLeaderboard(contestId, leaderboard, ttl = 300) {
        // Cache leaderboard for 5 minutes during contest
        const key = `leaderboard:${contestId}`;
        return await this.set(key, leaderboard, ttl);
    }

    async getLeaderboard(contestId) {
        const key = `leaderboard:${contestId}`;
        return await this.get(key);
    }

    async invalidateLeaderboard(contestId) {
        const key = `leaderboard:${contestId}`;
        return await this.delete(key);
    }

    // ============================================
    // USER PROFILE CACHING
    // ============================================

    async cacheUserProfile(userId, profile, ttl = 600) {
        // Cache user profile for 10 minutes
        const key = `user:${userId}`;
        return await this.set(key, profile, ttl);
    }

    async getUserProfile(userId) {
        const key = `user:${userId}`;
        return await this.get(key);
    }

    async invalidateUserProfile(userId) {
        const key = `user:${userId}`;
        return await this.delete(key);
    }

    // ============================================
    // PROBLEM CACHING
    // ============================================

    async cacheProblemList(page, limit, filters, problems, ttl = 3600) {
        // Cache problem lists for 1 hour
        const filterKey = JSON.stringify(filters || {});
        const hash = require('crypto').createHash('md5').update(filterKey).digest('hex');
        const key = `problems:${page}:${limit}:${hash}`;
        return await this.set(key, problems, ttl);
    }

    async getProblemList(page, limit, filters) {
        const filterKey = JSON.stringify(filters || {});
        const hash = require('crypto').createHash('md5').update(filterKey).digest('hex');
        const key = `problems:${page}:${limit}:${hash}`;
        return await this.get(key);
    }

    async invalidateProblemList() {
        return await this.clear('problems:*');
    }

    async cacheProblem(problemId, problem, ttl = 3600) {
        // Cache individual problem for 1 hour
        const key = `problem:${problemId}`;
        return await this.set(key, problem, ttl);
    }

    async getProblem(problemId) {
        const key = `problem:${problemId}`;
        return await this.get(key);
    }

    async invalidateProblem(problemId) {
        const key = `problem:${problemId}`;
        return await this.delete(key);
    }

    // ============================================
    // CONTEST CACHING
    // ============================================

    async cacheContest(contestId, contest, ttl = 1800) {
        // Cache contest for 30 minutes
        const key = `contest:${contestId}`;
        return await this.set(key, contest, ttl);
    }

    async getContest(contestId) {
        const key = `contest:${contestId}`;
        return await this.get(key);
    }

    async invalidateContest(contestId) {
        const key = `contest:${contestId}`;
        return await this.delete(key);
    }

    async cacheContestList(contests, ttl = 600) {
        // Cache contest list for 10 minutes
        const key = 'contests:list';
        return await this.set(key, contests, ttl);
    }

    async getContestList() {
        const key = 'contests:list';
        return await this.get(key);
    }

    async invalidateContestList() {
        const key = 'contests:list';
        return await this.delete(key);
    }

    // ============================================
    // STATISTICS CACHING
    // ============================================

    async cachePlatformStats(stats, ttl = 3600) {
        // Cache platform stats for 1 hour
        const key = 'stats:platform';
        return await this.set(key, stats, ttl);
    }

    async getPlatformStats() {
        const key = 'stats:platform';
        return await this.get(key);
    }

    async invalidatePlatformStats() {
        const key = 'stats:platform';
        return await this.delete(key);
    }

    // ============================================
    // RATE LIMITING
    // ============================================

    async incrementRequestCount(userId, limit = 100, window = 900) {
        // Rate limit: 100 requests per 15 minutes
        const key = `ratelimit:${userId}`;
        
        try {
            const count = await this.client.incr(key);
            
            if (count === 1) {
                await this.client.expire(key, window);
            }
            
            return {
                count,
                limit,
                remaining: Math.max(0, limit - count),
                resetTime: window
            };
        } catch (error) {
            console.error('[Cache] Rate limit error:', error);
            return null;
        }
    }

    // ============================================
    // SESSION CACHING
    // ============================================

    async cacheSession(sessionId, sessionData, ttl = 86400) {
        // Cache session for 24 hours
        const key = `session:${sessionId}`;
        return await this.set(key, sessionData, ttl);
    }

    async getSession(sessionId) {
        const key = `session:${sessionId}`;
        return await this.get(key);
    }

    async invalidateSession(sessionId) {
        const key = `session:${sessionId}`;
        return await this.delete(key);
    }

    // ============================================
    // BATCH OPERATIONS
    // ============================================

    async mget(...keys) {
        try {
            const values = await this.client.mGet(keys);
            return values.map(v => v ? JSON.parse(v) : null);
        } catch (error) {
            console.error('[Cache] MGET error:', error);
            return keys.map(() => null);
        }
    }

    async mset(keyValuePairs, ttl = this.defaultTTL) {
        try {
            for (const [key, value] of Object.entries(keyValuePairs)) {
                await this.set(key, value, ttl);
            }
            return true;
        } catch (error) {
            console.error('[Cache] MSET error:', error);
            return false;
        }
    }

    // ============================================
    // UTILITY
    // ============================================

    async getStats() {
        try {
            const info = await this.client.info();
            const used = await this.client.dbSize();
            
            return {
                connected: this.isConnected,
                info: info,
                keysCount: used
            };
        } catch (error) {
            console.error('[Cache] Stats error:', error);
            return null;
        }
    }

    // Singleton
    static instance = null;

    static getInstance(url) {
        if (!RedisCache.instance) {
            RedisCache.instance = new RedisCache(url);
        }
        return RedisCache.instance;
    }
}

module.exports = RedisCache;
