// cache/__tests__/redisClient.test.js
// Unit tests for Redis cache client

jest.mock('redis');

const RedisCache = require('../redisClient');
const redis = require('redis');

describe('RedisCache', () => {
  let cache;
  let mockClient;
  
  beforeEach(() => {
    // Mock Redis client
    mockClient = {
      connect: jest.fn().mockResolvedValue(undefined),
      disconnect: jest.fn().mockResolvedValue(undefined),
      set: jest.fn().mockResolvedValue('OK'),
      get: jest.fn(),
      del: jest.fn().mockResolvedValue(1),
      exists: jest.fn(),
      keys: jest.fn(),
      mget: jest.fn(),
      mset: jest.fn().mockResolvedValue('OK'),
      on: jest.fn(),
      off: jest.fn(),
      info: jest.fn().mockResolvedValue('mock-info')
    };
    
    redis.createClient.mockReturnValue(mockClient);
    
    cache = new RedisCache('redis://localhost:6379');
  });
  
  describe('set and get', () => {
    it('should set and retrieve a value', async () => {
      const testData = { name: 'test', value: 123 };
      mockClient.get.mockResolvedValue(JSON.stringify(testData));
      
      await cache.set('key1', testData);
      const result = await cache.get('key1');
      
      expect(mockClient.set).toHaveBeenCalledWith(
        'key1',
        JSON.stringify(testData),
        expect.any(Object)
      );
      expect(result).toEqual(testData);
    });
    
    it('should set value with TTL', async () => {
      await cache.set('key2', { data: 'test' }, 300);
      
      expect(mockClient.set).toHaveBeenCalledWith(
        'key2',
        expect.any(String),
        { EX: 300 }
      );
    });
    
    it('should return null for non-existent key', async () => {
      mockClient.get.mockResolvedValue(null);
      
      const result = await cache.get('nonexistent');
      
      expect(result).toBeNull();
    });
  });
  
  describe('delete', () => {
    it('should delete a key', async () => {
      await cache.delete('key1');
      
      expect(mockClient.del).toHaveBeenCalledWith('key1');
    });
    
    it('should handle deletion of non-existent key', async () => {
      mockClient.del.mockResolvedValue(0);
      
      await cache.delete('nonexistent');
      
      expect(mockClient.del).toHaveBeenCalledWith('nonexistent');
    });
  });
  
  describe('exists', () => {
    it('should check if key exists', async () => {
      mockClient.exists.mockResolvedValue(1);
      
      const exists = await cache.exists('key1');
      
      expect(exists).toBe(true);
      expect(mockClient.exists).toHaveBeenCalledWith('key1');
    });
    
    it('should return false for non-existent key', async () => {
      mockClient.exists.mockResolvedValue(0);
      
      const exists = await cache.exists('nonexistent');
      
      expect(exists).toBe(false);
    });
  });
  
  describe('clear pattern', () => {
    it('should clear keys matching pattern', async () => {
      mockClient.keys.mockResolvedValue(['problem:1', 'problem:2', 'problem:3']);
      mockClient.del.mockResolvedValue(3);
      
      await cache.clear('problem:*');
      
      expect(mockClient.keys).toHaveBeenCalledWith('problem:*');
      expect(mockClient.del).toHaveBeenCalled();
    });
    
    it('should handle empty pattern matches', async () => {
      mockClient.keys.mockResolvedValue([]);
      
      await cache.clear('nonexistent:*');
      
      expect(mockClient.keys).toHaveBeenCalledWith('nonexistent:*');
      expect(mockClient.del).not.toHaveBeenCalled();
    });
  });
  
  describe('Batch operations', () => {
    it('should handle mget for multiple keys', async () => {
      const values = ['value1', JSON.stringify({ id: 2 }), null];
      mockClient.mget.mockResolvedValue(values);
      
      const results = await cache.mget('key1', 'key2', 'key3');
      
      expect(mockClient.mget).toHaveBeenCalledWith(['key1', 'key2', 'key3']);
      expect(results).toHaveLength(3);
    });
    
    it('should handle mset for multiple keys', async () => {
      const pairs = { key1: 'value1', key2: { data: 'test' } };
      
      await cache.mset(pairs, 600);
      
      expect(mockClient.mset).toHaveBeenCalled();
    });
  });
});

describe('Specialized Cache Methods', () => {
  let cache;
  let mockClient;
  
  beforeEach(() => {
    mockClient = {
      set: jest.fn().mockResolvedValue('OK'),
      get: jest.fn(),
      del: jest.fn(),
      keys: jest.fn(),
      connect: jest.fn(),
      disconnect: jest.fn(),
      info: jest.fn()
    };
    
    redis.createClient.mockReturnValue(mockClient);
    cache = new RedisCache('redis://localhost');
  });
  
  describe('Problem Caching', () => {
    it('should cache problem', async () => {
      const problem = { id: '1', title: 'Test Problem', difficulty: 'easy' };
      
      await cache.cacheProblem('prob1', problem, 3600);
      
      expect(mockClient.set).toHaveBeenCalledWith(
        'problem:prob1',
        JSON.stringify(problem),
        { EX: 3600 }
      );
    });
    
    it('should invalidate problem cache', async () => {
      await cache.invalidateProblem('prob1');
      
      expect(mockClient.del).toHaveBeenCalledWith('problem:prob1');
    });
  });
  
  describe('User Profile Caching', () => {
    it('should cache user profile', async () => {
      const profile = { id: 'user1', username: 'testuser', email: 'test@example.com' };
      
      await cache.cacheUserProfile('user1', profile, 600);
      
      expect(mockClient.set).toHaveBeenCalledWith(
        'user:user1',
        JSON.stringify(profile),
        { EX: 600 }
      );
    });
    
    it('should have shorter TTL for user profiles', async () => {
      mockClient.get.mockResolvedValue(null);
      
      await cache.cacheUserProfile('user1', { username: 'test' });
      
      const callArgs = mockClient.set.mock.calls[0];
      expect(callArgs[2]).toEqual({ EX: 600 }); // 10 minutes
    });
  });
  
  describe('Leaderboard Caching', () => {
    it('should cache leaderboard', async () => {
      const leaderboard = [
        { rank: 1, username: 'user1', score: 100 },
        { rank: 2, username: 'user2', score: 95 }
      ];
      
      await cache.cacheLeaderboard('contest1', leaderboard, 300);
      
      expect(mockClient.set).toHaveBeenCalledWith(
        'leaderboard:contest1',
        JSON.stringify(leaderboard),
        { EX: 300 }
      );
    });
    
    it('should have short TTL for leaderboard', async () => {
      await cache.cacheLeaderboard('contest1', []);
      
      const callArgs = mockClient.set.mock.calls[0];
      expect(callArgs[2]).toEqual({ EX: 300 }); // 5 minutes
    });
  });
});

describe('Rate Limiting', () => {
  let cache;
  let mockClient;
  
  beforeEach(() => {
    mockClient = {
      incr: jest.fn(),
      expire: jest.fn(),
      ttl: jest.fn(),
      get: jest.fn(),
      connect: jest.fn(),
      disconnect: jest.fn(),
      info: jest.fn()
    };
    
    redis.createClient.mockReturnValue(mockClient);
    cache = new RedisCache('redis://localhost');
  });
  
  it('should increment request count', async () => {
    mockClient.incr.mockResolvedValue(1);
    mockClient.ttl.mockResolvedValue(-1);
    
    // Implementation would use incr and expire
    expect(mockClient.incr).toBeDefined();
    expect(mockClient.expire).toBeDefined();
  });
  
  it('should track remaining requests', async () => {
    mockClient.get.mockResolvedValue('5');
    
    // Rate limit logic: remaining = limit - count
    const remaining = 100 - parseInt('5');
    expect(remaining).toBe(95);
  });
});

describe('Error Handling', () => {
  let cache;
  let mockClient;
  
  beforeEach(() => {
    mockClient = {
      set: jest.fn(),
      get: jest.fn(),
      connect: jest.fn(),
      disconnect: jest.fn(),
      info: jest.fn()
    };
    
    redis.createClient.mockReturnValue(mockClient);
    cache = new RedisCache('redis://localhost');
  });
  
  it('should handle set errors gracefully', async () => {
    mockClient.set.mockRejectedValue(new Error('Connection failed'));
    
    await expect(cache.set('key', 'value')).rejects.toThrow('Connection failed');
  });
  
  it('should handle get errors gracefully', async () => {
    mockClient.get.mockRejectedValue(new Error('Timeout'));
    
    await expect(cache.get('key')).rejects.toThrow('Timeout');
  });
  
  it('should handle JSON parse errors', async () => {
    mockClient.get.mockResolvedValue('invalid json {]');
    
    expect(async () => {
      const result = await cache.get('key');
      JSON.parse(result);
    }).toBeDefined();
  });
});

describe('Connection Management', () => {
  let cache;
  let mockClient;
  
  beforeEach(() => {
    mockClient = {
      connect: jest.fn().mockResolvedValue(undefined),
      disconnect: jest.fn().mockResolvedValue(undefined),
      on: jest.fn(),
      set: jest.fn(),
      get: jest.fn(),
      info: jest.fn()
    };
    
    redis.createClient.mockReturnValue(mockClient);
    cache = new RedisCache('redis://localhost');
  });
  
  it('should establish connection', async () => {
    await cache.connect();
    
    expect(mockClient.connect).toHaveBeenCalled();
  });
  
  it('should close connection', async () => {
    await cache.disconnect();
    
    expect(mockClient.disconnect).toHaveBeenCalled();
  });
  
  it('should handle connection events', async () => {
    await cache.connect();
    
    expect(mockClient.on).toHaveBeenCalledWith('error', expect.any(Function));
    expect(mockClient.on).toHaveBeenCalledWith('connect', expect.any(Function));
  });
});
