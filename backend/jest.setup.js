// jest.setup.js
// Setup file that runs before all tests

// Set test environment
process.env.NODE_ENV = 'test';
process.env.MONGODB_URI = 'mongodb://localhost:27017/studyhub-test';
process.env.REDIS_HOST = 'localhost';
process.env.REDIS_PORT = 6379;
process.env.JWT_SECRET = 'test-secret-key-for-testing-only';
process.env.LOG_LEVEL = 'error';

// Suppress console logs during tests (optional)
// global.console = {
//   log: jest.fn(),
//   debug: jest.fn(),
//   info: jest.fn(),
//   warn: jest.fn(),
//   error: jest.fn(),
// };

// Setup default timeout
jest.setTimeout(10000);

// Mock external APIs by default
jest.mock('axios');

// Extend Jest matchers if needed
expect.extend({
  toBeValidEmail(received) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const pass = emailRegex.test(received);
    return {
      pass,
      message: () =>
        pass
          ? `expected ${received} not to be a valid email`
          : `expected ${received} to be a valid email`
    };
  },
  toBeValidJWT(received) {
    const jwtRegex = /^[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*$/;
    const pass = jwtRegex.test(received);
    return {
      pass,
      message: () =>
        pass
          ? `expected ${received} not to be a valid JWT`
          : `expected ${received} to be a valid JWT`
    };
  }
});

// Global test data
global.testUser = {
  id: '507f1f77bcf86cd799439011',
  username: 'testuser',
  email: 'test@example.com',
  password: 'TestPassword123!',
  role: 'user'
};

global.testProblem = {
  id: '507f1f77bcf86cd799439012',
  title: 'Test Problem',
  description: 'A test problem for unit testing',
  difficulty: 'easy',
  tags: ['arrays', 'strings'],
  timeLimit: 1000,
  memoryLimit: 256
};

global.testContest = {
  id: '507f1f77bcf86cd799439013',
  title: 'Test Contest',
  description: 'A test contest',
  startTime: new Date(),
  endTime: new Date(Date.now() + 3600000),
  problems: ['507f1f77bcf86cd799439012']
};

// Helper function to generate JWT token
global.generateTestToken = (userId = global.testUser.id, role = 'user') => {
  const jwt = require('jsonwebtoken');
  return jwt.sign({ id: userId, role }, process.env.JWT_SECRET, {
    expiresIn: '7d'
  });
};

// Helper function to create mock response
global.createMockResponse = () => {
  const response = {
    status: jest.fn().mockReturnThis(),
    json: jest.fn().mockReturnThis(),
    send: jest.fn().mockReturnThis(),
    end: jest.fn().mockReturnThis(),
    setHeader: jest.fn().mockReturnThis(),
    redirect: jest.fn().mockReturnThis(),
    locals: {}
  };
  return response;
};

// Helper function to create mock request
global.createMockRequest = (overrides = {}) => {
  return {
    body: {},
    params: {},
    query: {},
    headers: {},
    user: global.testUser,
    token: null,
    ...overrides
  };
};

// Helper function to create mock next function
global.createMockNext = () => {
  return jest.fn();
};

// Cleanup after each test
afterEach(() => {
  jest.clearAllMocks();
});

// Suppress console.error for expected errors during tests
const originalError = console.error;
beforeAll(() => {
  console.error = (...args) => {
    if (
      typeof args[0] === 'string' &&
      args[0].includes('expected error')
    ) {
      return;
    }
    originalError.call(console, ...args);
  };
});

afterAll(() => {
  console.error = originalError;
});
