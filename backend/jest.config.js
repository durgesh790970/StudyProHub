// jest.config.js
// Jest configuration for StudyHub backend tests

module.exports = {
  displayName: 'StudyHub Backend Tests',
  testEnvironment: 'node',
  
  // Root directory
  rootDir: './',
  
  // Test file patterns
  testMatch: [
    '**/__tests__/**/*.test.js',
    '**/?(*.)+(spec|test).js'
  ],
  
  // Directories to ignore
  testPathIgnorePatterns: [
    '/node_modules/',
    '/dist/',
    '/.git/'
  ],
  
  // Setup files (run before tests)
  setupFilesAfterEnv: ['./jest.setup.js'],
  
  // Coverage settings
  collectCoverageFrom: [
    'accounts/**/*.js',
    'config/**/*.js',
    'database/**/*.js',
    'cache/**/*.js',
    'jobs/**/*.js',
    '!**/__tests__/**',
    '!**/node_modules/**',
    '!**/*.config.js',
    '!**/main.js'
  ],
  
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 75,
      lines: 75,
      statements: 75
    }
  },
  
  // Transform files using babel
  transform: {
    '^.+\\.jsx?$': ['babel-jest', { rootMode: 'upward' }]
  },
  
  // Module name mapper (for aliases or mocks)
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/$1',
    '^@cache/(.*)$': '<rootDir>/cache/$1',
    '^@models/(.*)$': '<rootDir>/accounts/models.js',
    '^@utils/(.*)$': '<rootDir>/accounts/utils.js'
  },
  
  // Test timeout
  testTimeout: 10000,
  
  // Globals
  globals: {
    'NODE_ENV': 'test'
  },
  
  // Reporters
  reporters: [
    'default',
    [
      'jest-junit',
      {
        outputDirectory: './test-results',
        outputName: 'junit.xml',
        classNameTemplate: '{classname}',
        titleTemplate: '{title}',
        ancestorSeparator: ' › ',
        usePathAsClassName: true
      }
    ]
  ],
  
  // Detect open handles
  detectOpenHandles: false,
  
  // Force exit (useful for hanging processes)
  forceExit: true,
  
  // Verbose output
  verbose: true,
  
  // Clear mocks between tests
  clearMocks: true,
  
  // Restore mocks between tests
  restoreMocks: true,
  
  // Max workers
  maxWorkers: '50%'
};
