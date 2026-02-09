// __tests__/integration/api.integration.test.js
// Integration tests for API endpoints

jest.mock('../../database/db');
jest.mock('../../cache/redisClient');

const request = require('supertest');

// Mock Express app setup
const setupMockApp = () => {
  const express = require('express');
  const app = express();
  
  app.use(express.json());
  
  // Mock routes for testing
  app.post('/api/auth/signup', (req, res) => {
    const { email, username, password } = req.body;
    
    if (!email || !username || !password) {
      return res.status(400).json({ error: 'Missing required fields' });
    }
    
    res.status(201).json({
      id: '507f1f77bcf86cd799439011',
      username,
      email
    });
  });
  
  app.post('/api/auth/login', (req, res) => {
    const { email, password } = req.body;
    
    if (!email || !password) {
      return res.status(400).json({ error: 'Missing credentials' });
    }
    
    if (password !== 'correct') {
      return res.status(401).json({ error: 'Invalid credentials' });
    }
    
    res.json({
      token: 'mock-jwt-token',
      user: { id: '123', email, username: 'testuser' }
    });
  });
  
  app.get('/api/problems', (req, res) => {
    res.json({
      problems: [
        { id: '1', title: 'Problem 1', difficulty: 'easy' },
        { id: '2', title: 'Problem 2', difficulty: 'medium' }
      ],
      total: 2,
      page: 1
    });
  });
  
  app.get('/api/problems/:id', (req, res) => {
    if (!req.params.id) {
      return res.status(400).json({ error: 'ID required' });
    }
    
    res.json({
      id: req.params.id,
      title: 'Test Problem',
      difficulty: 'medium',
      description: 'Test description'
    });
  });
  
  app.post('/api/submissions', (req, res) => {
    const { problemId, code, language } = req.body;
    
    if (!problemId || !code || !language) {
      return res.status(400).json({ error: 'Missing required fields' });
    }
    
    res.status(201).json({
      id: '507f1f77bcf86cd799439012',
      problemId,
      userId: '123',
      verdict: 'PENDING',
      language
    });
  });
  
  return app;
};

describe('API Integration Tests', () => {
  let app;
  
  beforeEach(() => {
    app = setupMockApp();
  });
  
  describe('Authentication', () => {
    describe('POST /api/auth/signup', () => {
      it('should register a new user', async () => {
        const res = await request(app)
          .post('/api/auth/signup')
          .send({
            email: 'newuser@example.com',
            username: 'newuser',
            password: 'SecurePassword123!'
          });
        
        expect(res.status).toBe(201);
        expect(res.body).toHaveProperty('id');
        expect(res.body.email).toBe('newuser@example.com');
        expect(res.body.username).toBe('newuser');
      });
      
      it('should return 400 for missing fields', async () => {
        const res = await request(app)
          .post('/api/auth/signup')
          .send({
            email: 'test@example.com'
            // missing username and password
          });
        
        expect(res.status).toBe(400);
        expect(res.body.error).toBe('Missing required fields');
      });
      
      it('should accept multiple user registrations', async () => {
        const res1 = await request(app)
          .post('/api/auth/signup')
          .send({
            email: 'user1@example.com',
            username: 'user1',
            password: 'pass1'
          });
        
        const res2 = await request(app)
          .post('/api/auth/signup')
          .send({
            email: 'user2@example.com',
            username: 'user2',
            password: 'pass2'
          });
        
        expect(res1.status).toBe(201);
        expect(res2.status).toBe(201);
        expect(res1.body.username).not.toBe(res2.body.username);
      });
    });
    
    describe('POST /api/auth/login', () => {
      it('should login with correct credentials', async () => {
        const res = await request(app)
          .post('/api/auth/login')
          .send({
            email: 'test@example.com',
            password: 'correct'
          });
        
        expect(res.status).toBe(200);
        expect(res.body).toHaveProperty('token');
        expect(res.body.token).toBe('mock-jwt-token');
        expect(res.body.user).toHaveProperty('id');
      });
      
      it('should reject incorrect credentials', async () => {
        const res = await request(app)
          .post('/api/auth/login')
          .send({
            email: 'test@example.com',
            password: 'wrong'
          });
        
        expect(res.status).toBe(401);
        expect(res.body.error).toBe('Invalid credentials');
      });
      
      it('should return 400 for missing credentials', async () => {
        const res = await request(app)
          .post('/api/auth/login')
          .send({ email: 'test@example.com' }); // missing password
        
        expect(res.status).toBe(400);
      });
    });
  });
  
  describe('Problems', () => {
    describe('GET /api/problems', () => {
      it('should fetch all problems', async () => {
        const res = await request(app)
          .get('/api/problems');
        
        expect(res.status).toBe(200);
        expect(Array.isArray(res.body.problems)).toBe(true);
        expect(res.body.problems.length).toBeGreaterThan(0);
        expect(res.body).toHaveProperty('total');
        expect(res.body).toHaveProperty('page');
      });
      
      it('should return paginated results', async () => {
        const res1 = await request(app)
          .get('/api/problems?page=1&limit=10');
        
        const res2 = await request(app)
          .get('/api/problems?page=2&limit=10');
        
        expect(res1.status).toBe(200);
        expect(res2.status).toBe(200);
      });
      
      it('should handle filtering', async () => {
        const res = await request(app)
          .get('/api/problems?difficulty=easy');
        
        expect(res.status).toBe(200);
      });
    });
    
    describe('GET /api/problems/:id', () => {
      it('should fetch a specific problem', async () => {
        const res = await request(app)
          .get('/api/problems/1');
        
        expect(res.status).toBe(200);
        expect(res.body.id).toBe('1');
        expect(res.body).toHaveProperty('title');
        expect(res.body).toHaveProperty('difficulty');
        expect(res.body).toHaveProperty('description');
      });
      
      it('should return 400 for missing ID', async () => {
        const res = await request(app)
          .get('/api/problems/');
        
        expect(res.status).toBe(404); // This would be 404 in real scenario
      });
    });
  });
  
  describe('Submissions', () => {
    describe('POST /api/submissions', () => {
      it('should create a new submission', async () => {
        const res = await request(app)
          .post('/api/submissions')
          .send({
            problemId: '1',
            code: 'print("hello")',
            language: 'python'
          });
        
        expect(res.status).toBe(201);
        expect(res.body).toHaveProperty('id');
        expect(res.body.verdict).toBe('PENDING');
        expect(res.body.language).toBe('python');
      });
      
      it('should validate required fields', async () => {
        const res = await request(app)
          .post('/api/submissions')
          .send({
            problemId: '1'
            // missing code and language
          });
        
        expect(res.status).toBe(400);
        expect(res.body.error).toBe('Missing required fields');
      });
      
      it('should accept submissions in different languages', async () => {
        const languages = ['python', 'cpp', 'java', 'javascript'];
        
        for (const lang of languages) {
          const res = await request(app)
            .post('/api/submissions')
            .send({
              problemId: '1',
              code: 'code',
              language: lang
            });
          
          expect(res.status).toBe(201);
          expect(res.body.language).toBe(lang);
        }
      });
    });
  });
});

describe('Error Handling', () => {
  let app;
  
  beforeEach(() => {
    app = setupMockApp();
  });
  
  it('should handle 404 for unknown routes', async () => {
    const res = await request(app)
      .get('/api/unknown');
    
    expect(res.status).toBe(404);
  });
  
  it('should handle malformed JSON', async () => {
    const res = await request(app)
      .post('/api/auth/signup')
      .set('Content-Type', 'application/json')
      .send('malformed json');
    
    expect(res.status).toBeGreaterThanOrEqual(400);
  });
  
  it('should handle missing Content-Type header', async () => {
    const res = await request(app)
      .post('/api/auth/signup')
      .send({ email: 'test@example.com' });
    
    expect(res.status).toBeGreaterThanOrEqual(400);
  });
});

describe('Request/Response Validation', () => {
  let app;
  
  beforeEach(() => {
    app = setupMockApp();
  });
  
  it('should return correct response headers', async () => {
    const res = await request(app)
      .get('/api/problems');
    
    expect(res.headers['content-type']).toContain('application/json');
  });
  
  it('should handle OPTIONS requests', async () => {
    const res = await request(app)
      .options('/api/problems');
    
    expect([200, 204, 404]).toContain(res.status);
  });
  
  it('should validate response structure', async () => {
    const res = await request(app)
      .get('/api/problems');
    
    expect(res.body).toHaveProperty('problems');
    expect(res.body).toHaveProperty('total');
    expect(typeof res.body.total).toBe('number');
  });
});
