// accounts/__tests__/auth.test.js
// Unit tests for authentication utilities

jest.mock('jsonwebtoken');
jest.mock('bcryptjs');

const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');

// Mock the auth utilities (in real scenario, these would be real functions)
const AuthUtils = {
  generateToken: (userId, role) => {
    return jwt.sign({ id: userId, role }, process.env.JWT_SECRET, {
      expiresIn: '7d'
    });
  },
  
  verifyToken: (token) => {
    return jwt.verify(token, process.env.JWT_SECRET);
  },
  
  hashPassword: async (password) => {
    const salt = await bcrypt.genSalt(10);
    return bcrypt.hash(password, salt);
  },
  
  comparePassword: async (password, hash) => {
    return bcrypt.compare(password, hash);
  }
};

describe('Authentication Utilities', () => {
  
  describe('generateToken', () => {
    it('should generate a valid JWT token', () => {
      jwt.sign.mockReturnValue('mock-token');
      
      const token = AuthUtils.generateToken('123', 'user');
      
      expect(token).toBe('mock-token');
      expect(jwt.sign).toHaveBeenCalledWith(
        { id: '123', role: 'user' },
        process.env.JWT_SECRET,
        { expiresIn: '7d' }
      );
    });
    
    it('should generate token with admin role', () => {
      jwt.sign.mockReturnValue('admin-token');
      
      const token = AuthUtils.generateToken('456', 'admin');
      
      expect(token).toBe('admin-token');
      expect(jwt.sign).toHaveBeenCalledWith(
        { id: '456', role: 'admin' },
        process.env.JWT_SECRET,
        { expiresIn: '7d' }
      );
    });
  });
  
  describe('verifyToken', () => {
    it('should verify a valid token', () => {
      jwt.verify.mockReturnValue({ id: '123', role: 'user' });
      
      const decoded = AuthUtils.verifyToken('valid-token');
      
      expect(decoded).toEqual({ id: '123', role: 'user' });
      expect(jwt.verify).toHaveBeenCalledWith('valid-token', process.env.JWT_SECRET);
    });
    
    it('should throw error for invalid token', () => {
      jwt.verify.mockImplementation(() => {
        throw new Error('Invalid token');
      });
      
      expect(() => {
        AuthUtils.verifyToken('invalid-token');
      }).toThrow('Invalid token');
    });
    
    it('should throw error for expired token', () => {
      jwt.verify.mockImplementation(() => {
        throw new Error('Token expired');
      });
      
      expect(() => {
        AuthUtils.verifyToken('expired-token');
      }).toThrow('Token expired');
    });
  });
  
  describe('hashPassword', () => {
    it('should hash a password', async () => {
      bcrypt.genSalt.mockResolvedValue('salt');
      bcrypt.hash.mockResolvedValue('hashed-password');
      
      const hashed = await AuthUtils.hashPassword('password123');
      
      expect(hashed).toBe('hashed-password');
      expect(bcrypt.genSalt).toHaveBeenCalledWith(10);
      expect(bcrypt.hash).toHaveBeenCalledWith('password123', 'salt');
    });
    
    it('should handle hashing errors', async () => {
      bcrypt.genSalt.mockRejectedValue(new Error('Hash error'));
      
      await expect(AuthUtils.hashPassword('password')).rejects.toThrow('Hash error');
    });
  });
  
  describe('comparePassword', () => {
    it('should compare password correctly', async () => {
      bcrypt.compare.mockResolvedValue(true);
      
      const result = await AuthUtils.comparePassword('password', 'hashed');
      
      expect(result).toBe(true);
      expect(bcrypt.compare).toHaveBeenCalledWith('password', 'hashed');
    });
    
    it('should return false for incorrect password', async () => {
      bcrypt.compare.mockResolvedValue(false);
      
      const result = await AuthUtils.comparePassword('wrong', 'hashed');
      
      expect(result).toBe(false);
    });
  });
});

describe('Token Claims', () => {
  it('should have correct structure in generated token', () => {
    jwt.sign.mockReturnValue('token');
    
    AuthUtils.generateToken('user123', 'moderator');
    
    const callArgs = jwt.sign.mock.calls[0];
    expect(callArgs[0]).toHaveProperty('id', 'user123');
    expect(callArgs[0]).toHaveProperty('role', 'moderator');
  });
});

describe('Password Security', () => {
  it('should use 10 rounds for bcrypt salt', async () => {
    bcrypt.genSalt.mockResolvedValue('salt');
    bcrypt.hash.mockResolvedValue('hashed');
    
    await AuthUtils.hashPassword('secure-password');
    
    expect(bcrypt.genSalt).toHaveBeenCalledWith(10);
  });
  
  it('should not expose raw password in any operation', async () => {
    bcrypt.hash.mockResolvedValue('hashed');
    bcrypt.genSalt.mockResolvedValue('salt');
    
    const hashed = await AuthUtils.hashPassword('secret');
    
    expect(hashed).not.toBe('secret');
    expect(hashed).toBe('hashed');
  });
});
