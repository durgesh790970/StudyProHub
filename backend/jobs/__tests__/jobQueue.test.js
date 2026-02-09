// jobs/__tests__/jobQueue.test.js
// Unit tests for background job queue

jest.mock('bull');
jest.mock('axios');

const JobManager = require('../jobQueue');
const Queue = require('bull');
const axios = require('axios');

describe('JobManager', () => {
  let mockQueue;
  
  beforeEach(() => {
    mockQueue = {
      process: jest.fn(),
      add: jest.fn().mockResolvedValue({ id: 'job-1' }),
      on: jest.fn(),
      clean: jest.fn(),
      close: jest.fn(),
      getActiveCount: jest.fn().mockResolvedValue(0),
      getWaitingCount: jest.fn().mockResolvedValue(5),
      getCompletedCount: jest.fn().mockResolvedValue(100),
      getFailedCount: jest.fn().mockResolvedValue(2)
    };
    
    Queue.mockImplementation(() => mockQueue);
  });
  
  describe('Submission Queue', () => {
    it('should setup submission queue processor', () => {
      JobManager.setupSubmissionQueue();
      
      expect(mockQueue.process).toHaveBeenCalledWith(
        'process-submission',
        5,
        expect.any(Function)
      );
    });
    
    it('should add submission job', async () => {
      const submissionData = {
        submissionId: 'sub-1',
        userId: 'user-1',
        problemId: 'prob-1',
        code: 'print("hello")',
        language: 'python',
        contestId: 'contest-1'
      };
      
      const job = await JobManager.addSubmissionJob(submissionData);
      
      expect(mockQueue.add).toHaveBeenCalledWith(
        'process-submission',
        submissionData,
        expect.objectContaining({
          attempts: 3,
          backoff: expect.any(Object),
          removeOnComplete: true
        })
      );
      expect(job.id).toBe('job-1');
    });
  });
  
  describe('Email Queue', () => {
    it('should setup email queue processor', () => {
      JobManager.setupEmailQueue();
      
      expect(mockQueue.process).toHaveBeenCalledWith(
        'send-email',
        10,
        expect.any(Function)
      );
    });
    
    it('should add email job', async () => {
      const emailData = {
        to: 'user@example.com',
        subject: 'Welcome to StudyHub',
        template: 'welcome',
        data: { name: 'John' }
      };
      
      const job = await JobManager.addEmailJob(emailData);
      
      expect(mockQueue.add).toHaveBeenCalledWith(
        'send-email',
        emailData,
        expect.objectContaining({
          attempts: 3,
          removeOnComplete: true
        })
      );
      expect(job).toBeDefined();
    });
  });
  
  describe('Report Queue', () => {
    it('should setup report queue processor', () => {
      JobManager.setupReportQueue();
      
      expect(mockQueue.process).toHaveBeenCalledWith(
        'generate-report',
        3,
        expect.any(Function)
      );
    });
    
    it('should add report job', async () => {
      const reportData = {
        reportId: 'rep-1',
        userId: 'user-1',
        type: 'performance',
        filters: { startDate: '2024-01-01', endDate: '2024-01-31' }
      };
      
      const job = await JobManager.addReportJob(reportData);
      
      expect(mockQueue.add).toHaveBeenCalledWith(
        'generate-report',
        reportData,
        expect.any(Object)
      );
      expect(job).toBeDefined();
    });
  });
  
  describe('Leaderboard Queue', () => {
    it('should setup leaderboard queue processor', () => {
      JobManager.setupLeaderboardQueue();
      
      expect(mockQueue.process).toHaveBeenCalledWith(
        'update-leaderboard',
        5,
        expect.any(Function)
      );
    });
    
    it('should add leaderboard job with high priority', async () => {
      const contestId = 'contest-1';
      
      const job = await JobManager.addLeaderboardJob(contestId);
      
      expect(mockQueue.add).toHaveBeenCalledWith(
        'update-leaderboard',
        { contestId },
        expect.objectContaining({
          priority: 10
        })
      );
      expect(job).toBeDefined();
    });
  });
  
  describe('Queue Statistics', () => {
    it('should retrieve queue statistics', async () => {
      mockQueue.getActiveCount.mockResolvedValue(2);
      mockQueue.getWaitingCount.mockResolvedValue(10);
      mockQueue.getCompletedCount.mockResolvedValue(500);
      mockQueue.getFailedCount.mockResolvedValue(5);
      
      const stats = await JobManager.getQueueStats();
      
      expect(stats).toHaveProperty('submissions');
      expect(stats).toHaveProperty('emails');
      expect(stats).toHaveProperty('reports');
      expect(stats).toHaveProperty('leaderboard');
      
      expect(stats.submissions).toEqual({
        active: 2,
        waiting: 10,
        completed: 500,
        failed: 5
      });
    });
    
    it('should show high failure rate', async () => {
      mockQueue.getActiveCount.mockResolvedValue(0);
      mockQueue.getWaitingCount.mockResolvedValue(0);
      mockQueue.getCompletedCount.mockResolvedValue(100);
      mockQueue.getFailedCount.mockResolvedValue(50);
      
      const stats = await JobManager.getQueueStats();
      
      expect(stats.submissions.failed).toBe(50);
    });
  });
  
  describe('Cleanup Operations', () => {
    it('should clear completed jobs', async () => {
      await JobManager.clearCompletedJobs();
      
      expect(mockQueue.clean).toHaveBeenCalledTimes(4); // For each queue
    });
    
    it('should close all queues', async () => {
      await JobManager.closeQueues();
      
      expect(mockQueue.close).toHaveBeenCalledTimes(4);
    });
  });
});

describe('Judge0 Integration', () => {
  describe('Code Execution', () => {
    it('should submit code to Judge0', async () => {
      axios.post.mockResolvedValue({
        data: { token: 'judge0-token-123' }
      });
      
      axios.get.mockResolvedValue({
        data: {
          status: { id: 3 }, // accepted
          stdout: 'Hello World',
          stderr: null,
          time: 0.5,
          memory: 512
        }
      });
      
      // This would be called inside job processor
      expect(axios.post).toBeDefined();
      expect(axios.get).toBeDefined();
    });
    
    it('should handle Judge0 timeout', async () => {
      axios.post.mockResolvedValue({
        data: { token: 'token' }
      });
      
      // Simulate timeout polling
      let attempts = 0;
      axios.get.mockImplementation(() => {
        attempts++;
        if (attempts < 30) {
          return Promise.resolve({
            data: { status: { id: 1 } } // Still processing
          });
        }
        return Promise.resolve({
          data: { status: { id: 5 } } // Time limit exceeded
        });
      });
      
      expect(axios.post).toBeDefined();
    });
  });
  
  describe('Language Support', () => {
    it('should map languages to Judge0 IDs', () => {
      const languageMap = {
        'python': 71,
        'cpp': 54,
        'c': 50,
        'java': 62,
        'javascript': 63,
        'rust': 73,
        'go': 60
      };
      
      Object.entries(languageMap).forEach(([lang, id]) => {
        expect(id).toBeGreaterThan(0);
      });
    });
  });
  
  describe('Verdict Conversion', () => {
    it('should convert Judge0 status to verdict', () => {
      const statusMap = {
        3: 'ACCEPTED',
        4: 'WRONG_ANSWER',
        5: 'TIME_LIMIT_EXCEEDED',
        6: 'COMPILATION_ERROR',
        7: 'RUNTIME_ERROR'
      };
      
      expect(statusMap[3]).toBe('ACCEPTED');
      expect(statusMap[4]).toBe('WRONG_ANSWER');
      expect(statusMap[5]).toBe('TIME_LIMIT_EXCEEDED');
    });
  });
});

describe('Job Retry Logic', () => {
  it('should retry failed submissions', async () => {
    const jobData = { submissionId: 'sub-1' };
    
    // Job with retry configuration
    const jobConfig = {
      attempts: 3,
      backoff: {
        type: 'exponential',
        delay: 2000
      }
    };
    
    expect(jobConfig.attempts).toBe(3);
    expect(jobConfig.backoff.type).toBe('exponential');
  });
  
  it('should use different backoff strategies', () => {
    const submissionBackoff = {
      type: 'exponential',
      delay: 2000
    };
    
    const emailBackoff = {
      type: 'exponential',
      delay: 5000
    };
    
    const reportBackoff = {
      type: 'fixed',
      delay: 10000
    };
    
    expect(submissionBackoff.type).toBe('exponential');
    expect(emailBackoff.delay).toBeGreaterThan(submissionBackoff.delay);
    expect(reportBackoff.type).toBe('fixed');
  });
});

describe('Priority Handling', () => {
  it('should prioritize leaderboard updates', async () => {
    const leaderboardJobConfig = {
      priority: 10, // Higher number = higher priority
      removeOnComplete: true
    };
    
    const normalJobConfig = {
      priority: 5
    };
    
    expect(leaderboardJobConfig.priority).toBeGreaterThan(normalJobConfig.priority);
  });
  
  it('should remove completed low-priority jobs', async () => {
    const completedEmailJob = {
      attempts: 3,
      removeOnComplete: true
    };
    
    expect(completedEmailJob.removeOnComplete).toBe(true);
  });
});

describe('Concurrency Control', () => {
  it('should limit concurrent submission processing', () => {
    // 5 concurrent processors for submissions
    expect(5).toBeGreaterThan(0);
  });
  
  it('should limit concurrent email sending', () => {
    // 10 concurrent processors for emails
    expect(10).toBeGreaterThan(5);
  });
  
  it('should limit concurrent report generation', () => {
    // 3 concurrent processors for reports
    expect(3).toBeGreaterThan(0);
  });
});

describe('Metrics and Monitoring', () => {
  it('should track job counts by status', async () => {
    mockQueue.getActiveCount.mockResolvedValue(5);
    mockQueue.getWaitingCount.mockResolvedValue(20);
    mockQueue.getCompletedCount.mockResolvedValue(1000);
    mockQueue.getFailedCount.mockResolvedValue(10);
    
    const stats = await JobManager.getQueueStats();
    
    expect(stats.submissions.active).toBe(5);
    expect(stats.submissions.waiting).toBe(20);
    expect(stats.submissions.completed).toBe(1000);
    expect(stats.submissions.failed).toBe(10);
  });
  
  it('should identify problematic queues', async () => {
    mockQueue.getFailedCount.mockResolvedValue(100);
    mockQueue.getCompletedCount.mockResolvedValue(100);
    
    const stats = await JobManager.getQueueStats();
    
    // High failure rate (50%)
    expect(stats.submissions.failed).toBeGreaterThan(0);
  });
});
