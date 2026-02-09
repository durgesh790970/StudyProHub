// backend/cache/cacheMiddleware.js
// Caching middleware for Express routes

const RedisCache = require('./redisClient');

class CacheMiddleware {
    constructor() {
        this.cache = RedisCache.getInstance();
    }

    // Middleware to cache GET responses
    cacheGetResponse(ttl = 3600) {
        return async (req, res, next) => {
            // Only cache GET requests
            if (req.method !== 'GET') {
                return next();
            }

            // Don't cache if not authenticated when needed
            if (req.headers.authorization && !req.user) {
                return next();
            }

            try {
                const cacheKey = this.generateCacheKey(req);
                const cachedResponse = await this.cache.get(cacheKey);

                if (cachedResponse) {
                    console.log(`[Cache] Hit for ${req.path}`);
                    return res.json(cachedResponse);
                }

                console.log(`[Cache] Miss for ${req.path}`);

                // Override res.json to cache the response
                const originalJson = res.json.bind(res);
                res.json = function(data) {
                    if (res.statusCode === 200) {
                        this.cache.set(cacheKey, data, ttl);
                    }
                    return originalJson(data);
                }.bind({ cache: this.cache });

                next();
            } catch (error) {
                console.error('[Cache] Middleware error:', error);
                next();
            }
        };
    }

    // Specific cache for problems list
    cacheProblemsList(ttl = 3600) {
        return async (req, res, next) => {
            if (req.method !== 'GET' || !req.path.startsWith('/api/problems')) {
                return next();
            }

            try {
                const { page = 1, limit = 20, difficulty, search, tags } = req.query;
                const filters = { difficulty, search, tags };

                const cached = await this.cache.getProblemList(page, limit, filters);
                if (cached) {
                    console.log('[Cache] Problems list hit');
                    return res.json(cached);
                }

                const originalJson = res.json.bind(res);
                res.json = function(data) {
                    if (res.statusCode === 200) {
                        this.cache.cacheProblemsList(data, ttl);
                    }
                    return originalJson(data);
                }.bind({ cache: this.cache });

                next();
            } catch (error) {
                console.error('[Cache] Problems middleware error:', error);
                next();
            }
        };
    }

    // Specific cache for user profile
    cacheUserProfile(ttl = 600) {
        return async (req, res, next) => {
            if (req.method !== 'GET' || !req.path.match(/\/api\/users\/\w+/)) {
                return next();
            }

            try {
                const userId = req.params.id;
                const cached = await this.cache.getUserProfile(userId);
                
                if (cached) {
                    console.log('[Cache] User profile hit');
                    return res.json(cached);
                }

                const originalJson = res.json.bind(res);
                res.json = function(data) {
                    if (res.statusCode === 200) {
                        this.cache.cacheUserProfile(userId, data, ttl);
                    }
                    return originalJson(data);
                }.bind({ cache: this.cache });

                next();
            } catch (error) {
                console.error('[Cache] User profile middleware error:', error);
                next();
            }
        };
    }

    // Specific cache for leaderboard
    cacheLeaderboard(ttl = 300) {
        return async (req, res, next) => {
            if (req.method !== 'GET' || !req.path.startsWith('/api/leaderboard')) {
                return next();
            }

            try {
                const contestId = req.query.contestId || 'global';
                const page = req.query.page || 1;
                const cacheKey = `leaderboard:${contestId}:${page}`;

                const cached = await this.cache.get(cacheKey);
                if (cached) {
                    console.log('[Cache] Leaderboard hit');
                    return res.json(cached);
                }

                const originalJson = res.json.bind(res);
                res.json = function(data) {
                    if (res.statusCode === 200) {
                        this.cache.set(cacheKey, data, ttl);
                    }
                    return originalJson(data);
                }.bind({ cache: this.cache });

                next();
            } catch (error) {
                console.error('[Cache] Leaderboard middleware error:', error);
                next();
            }
        };
    }

    // Invalid cache when data is modified
    invalidateCache(pattern) {
        return async (req, res, next) => {
            try {
                // Only invalidate on POST/PUT/DELETE
                if (['POST', 'PUT', 'DELETE'].includes(req.method)) {
                    await this.cache.clear(pattern);
                    console.log(`[Cache] Invalidated pattern: ${pattern}`);
                }
            } catch (error) {
                console.error('[Cache] Invalidation error:', error);
            }
            next();
        };
    }

    // Invalidate specific resources
    invalidateProblem(req, res, next) {
        const problemId = req.params.id;
        this.cache.invalidateProblem(problemId);
        this.cache.clear('problems:*');
        next();
    }

    invalidateContest(req, res, next) {
        const contestId = req.params.id;
        this.cache.invalidateContest(contestId);
        this.cache.invalidateLeaderboard(contestId);
        this.cache.invalidateContestList();
        next();
    }

    invalidateUser(req, res, next) {
        const userId = req.params.id;
        this.cache.invalidateUserProfile(userId);
        this.cache.clear('leaderboard:*');
        next();
    }

    generateCacheKey(req) {
        const base = `${req.method}:${req.path}`;
        const query = Object.keys(req.query || {})
            .sort()
            .map(key => `${key}=${req.query[key]}`)
            .join('&');
        
        return query ? `${base}?${query}` : base;
    }

    // Singleton
    static instance = null;

    static getInstance() {
        if (!CacheMiddleware.instance) {
            CacheMiddleware.instance = new CacheMiddleware();
        }
        return CacheMiddleware.instance;
    }
}

module.exports = CacheMiddleware;
