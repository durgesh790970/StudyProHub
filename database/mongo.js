// MongoDB Database Schema for Youtube Manage Application
// Generated: February 5, 2026
// This file shows the MongoDB collection structure and sample documents

// ============================================================
// USERS COLLECTION
// ============================================================
db.createCollection("users", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["username", "email", "password", "createdAt"],
      properties: {
        _id: { bsonType: "objectId" },
        username: { 
          bsonType: "string",
          description: "Unique username"
        },
        email: { 
          bsonType: "string",
          description: "Unique email address"
        },
        password: { 
          bsonType: "string",
          description: "Hashed password"
        },
        firstName: { bsonType: "string" },
        lastName: { bsonType: "string" },
        phone: { bsonType: "string" },
        profilePicture: { bsonType: "string" },
        bio: { bsonType: "string" },
        location: { bsonType: "string" },
        isActive: { bsonType: "bool", description: "Account active status" },
        isStaff: { bsonType: "bool", description: "Admin/Staff status" },
        isSuperuser: { bsonType: "bool", description: "Superuser status" },
        createdAt: { bsonType: "date" },
        updatedAt: { bsonType: "date" },
        lastLogin: { bsonType: "date" }
      }
    }
  }
});

// Create indexes for users
db.users.createIndex({ username: 1 }, { unique: true });
db.users.createIndex({ email: 1 }, { unique: true });
db.users.createIndex({ isActive: 1 });

// ============================================================
// MOCK TESTS COLLECTION
// ============================================================
db.createCollection("mockTests", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["userId", "title", "createdAt"],
      properties: {
        _id: { bsonType: "objectId" },
        userId: { bsonType: "objectId", description: "Reference to user" },
        title: { bsonType: "string" },
        description: { bsonType: "string" },
        durationMinutes: { bsonType: "int" },
        difficultyLevel: { 
          enum: ["easy", "medium", "hard"],
          description: "Test difficulty level"
        },
        category: { 
          enum: ["technical", "hr", "aptitude"],
          description: "Test category"
        },
        startTime: { bsonType: "date" },
        endTime: { bsonType: "date" },
        score: { bsonType: "int" },
        maxScore: { bsonType: "int" },
        status: { 
          enum: ["not_started", "in_progress", "completed"],
          description: "Test status"
        },
        createdAt: { bsonType: "date" },
        updatedAt: { bsonType: "date" }
      }
    }
  }
});

db.mockTests.createIndex({ userId: 1 });
db.mockTests.createIndex({ status: 1 });
db.mockTests.createIndex({ createdAt: 1 });

// ============================================================
// QUESTIONS COLLECTION
// ============================================================
db.createCollection("questions", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["title", "category", "questionType"],
      properties: {
        _id: { bsonType: "objectId" },
        title: { bsonType: "string" },
        description: { bsonType: "string" },
        category: { bsonType: "string" },
        difficultyLevel: { enum: ["easy", "medium", "hard"] },
        questionType: { 
          enum: ["multiple_choice", "essay", "coding", "true_false"],
          description: "Type of question"
        },
        marks: { bsonType: "int", minimum: 1 },
        options: { 
          bsonType: "array",
          items: { bsonType: "string" },
          description: "Answer options for MCQ"
        },
        correctAnswer: { bsonType: "string" },
        explanation: { bsonType: "string" },
        codeTemplate: { bsonType: "string", description: "For coding questions" },
        createdAt: { bsonType: "date" },
        updatedAt: { bsonType: "date" }
      }
    }
  }
});

db.questions.createIndex({ category: 1 });
db.questions.createIndex({ difficultyLevel: 1 });
db.questions.createIndex({ questionType: 1 });

// ============================================================
// TEST RESULTS COLLECTION
// ============================================================
db.createCollection("testResults", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["userId", "totalQuestions"],
      properties: {
        _id: { bsonType: "objectId" },
        userId: { bsonType: "objectId" },
        testId: { bsonType: "objectId" },
        totalQuestions: { bsonType: "int" },
        correctAnswers: { bsonType: "int" },
        wrongAnswers: { bsonType: "int" },
        skippedQuestions: { bsonType: "int" },
        score: { bsonType: "double" },
        percentage: { bsonType: "double" },
        timeSpentSeconds: { bsonType: "int" },
        status: { enum: ["passed", "failed"] },
        userAnswers: {
          bsonType: "array",
          items: {
            bsonType: "object",
            properties: {
              questionId: { bsonType: "objectId" },
              selectedAnswer: { bsonType: "string" },
              isCorrect: { bsonType: "bool" },
              timeSpent: { bsonType: "int" }
            }
          }
        },
        completedAt: { bsonType: "date" },
        createdAt: { bsonType: "date" }
      }
    }
  }
});

db.testResults.createIndex({ userId: 1 });
db.testResults.createIndex({ testId: 1 });
db.testResults.createIndex({ createdAt: 1 });

// ============================================================
// TRANSACTIONS COLLECTION
// ============================================================
db.createCollection("transactions", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["userId", "amount", "status"],
      properties: {
        _id: { bsonType: "objectId" },
        userId: { bsonType: "objectId" },
        amount: { bsonType: "decimal128" },
        currency: { bsonType: "string", default: "USD" },
        transactionType: { 
          enum: ["payment", "refund", "subscription"],
          description: "Type of transaction"
        },
        paymentMethod: { bsonType: "string" },
        status: { 
          enum: ["pending", "completed", "failed", "cancelled"],
          description: "Transaction status"
        },
        referenceId: { bsonType: "string" },
        description: { bsonType: "string" },
        receiptUrl: { bsonType: "string" },
        metadata: { bsonType: "object" },
        createdAt: { bsonType: "date" },
        updatedAt: { bsonType: "date" }
      }
    }
  }
});

db.transactions.createIndex({ userId: 1 });
db.transactions.createIndex({ status: 1 });
db.transactions.createIndex({ referenceId: 1 }, { unique: true });

// ============================================================
// COMPANIES COLLECTION
// ============================================================
db.createCollection("companies", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["name"],
      properties: {
        _id: { bsonType: "objectId" },
        name: { bsonType: "string" },
        description: { bsonType: "string" },
        logoUrl: { bsonType: "string" },
        websiteUrl: { bsonType: "string" },
        location: { bsonType: "string" },
        industry: { bsonType: "string" },
        placementPapers: { bsonType: "array" },
        createdAt: { bsonType: "date" },
        updatedAt: { bsonType: "date" }
      }
    }
  }
});

db.companies.createIndex({ name: 1 }, { unique: true });

// ============================================================
// PLACEMENT PAPERS COLLECTION
// ============================================================
db.createCollection("placementPapers", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["companyId", "title"],
      properties: {
        _id: { bsonType: "objectId" },
        companyId: { bsonType: "objectId" },
        title: { bsonType: "string" },
        year: { bsonType: "int" },
        semester: { bsonType: "string" },
        pdfUrl: { bsonType: "string" },
        difficultyLevel: { enum: ["easy", "medium", "hard"] },
        questions: { bsonType: "array" },
        createdAt: { bsonType: "date" }
      }
    }
  }
});

db.placementPapers.createIndex({ companyId: 1 });

// ============================================================
// JOB APPLICATIONS COLLECTION
// ============================================================
db.createCollection("jobApplications", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["userId", "companyId"],
      properties: {
        _id: { bsonType: "objectId" },
        userId: { bsonType: "objectId" },
        companyId: { bsonType: "objectId" },
        jobTitle: { bsonType: "string" },
        salaryOffered: { bsonType: "decimal128" },
        status: { 
          enum: ["applied", "rejected", "offered", "accepted"],
          description: "Application status"
        },
        appliedAt: { bsonType: "date" },
        responseDate: { bsonType: "date" }
      }
    }
  }
});

db.jobApplications.createIndex({ userId: 1 });
db.jobApplications.createIndex({ companyId: 1 });

// ============================================================
// INTERVIEW SESSIONS COLLECTION
// ============================================================
db.createCollection("interviewSessions", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["userId"],
      properties: {
        _id: { bsonType: "objectId" },
        userId: { bsonType: "objectId" },
        companyId: { bsonType: "objectId" },
        sessionType: { enum: ["technical", "hr", "coding"] },
        durationMinutes: { bsonType: "int" },
        feedback: { bsonType: "string" },
        rating: { bsonType: "int", minimum: 1, maximum: 5 },
        scheduledAt: { bsonType: "date" },
        startedAt: { bsonType: "date" },
        endedAt: { bsonType: "date" },
        recordingUrl: { bsonType: "string" },
        createdAt: { bsonType: "date" }
      }
    }
  }
});

db.interviewSessions.createIndex({ userId: 1 });
db.interviewSessions.createIndex({ companyId: 1 });

// ============================================================
// FEEDBACK COLLECTION
// ============================================================
db.createCollection("feedback", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["userId", "title", "message"],
      properties: {
        _id: { bsonType: "objectId" },
        userId: { bsonType: "objectId" },
        feedbackType: { 
          enum: ["bug_report", "feature_request", "general"],
          description: "Type of feedback"
        },
        title: { bsonType: "string" },
        message: { bsonType: "string" },
        rating: { bsonType: "int", minimum: 1, maximum: 5 },
        status: { 
          enum: ["pending", "reviewed", "resolved"],
          description: "Feedback status"
        },
        attachments: { bsonType: "array" },
        createdAt: { bsonType: "date" },
        updatedAt: { bsonType: "date" }
      }
    }
  }
});

db.feedback.createIndex({ userId: 1 });
db.feedback.createIndex({ status: 1 });

// ============================================================
// ITEMS/PRODUCTS COLLECTION
// ============================================================
db.createCollection("items", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["name", "price"],
      properties: {
        _id: { bsonType: "objectId" },
        name: { bsonType: "string" },
        description: { bsonType: "string" },
        price: { bsonType: "decimal128" },
        itemType: { 
          enum: ["course", "test_pack", "premium_membership"],
          description: "Type of item"
        },
        quantityAvailable: { bsonType: "int" },
        createdAt: { bsonType: "date" },
        updatedAt: { bsonType: "date" }
      }
    }
  }
});

// ============================================================
// USER PURCHASES COLLECTION
// ============================================================
db.createCollection("userPurchases", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["userId", "itemId"],
      properties: {
        _id: { bsonType: "objectId" },
        userId: { bsonType: "objectId" },
        itemId: { bsonType: "objectId" },
        transactionId: { bsonType: "objectId" },
        quantity: { bsonType: "int", default: 1 },
        purchaseDate: { bsonType: "date" },
        expiryDate: { bsonType: "date" }
      }
    }
  }
});

db.userPurchases.createIndex({ userId: 1 });
db.userPurchases.createIndex({ itemId: 1 });

// ============================================================
// B.TECH CONTENT COLLECTION
// ============================================================
db.createCollection("bTechContent", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["semesterNumber", "subjectName"],
      properties: {
        _id: { bsonType: "objectId" },
        semesterNumber: { bsonType: "int" },
        branch: { bsonType: "string" },
        subjectName: { bsonType: "string" },
        contentType: { enum: ["pdf", "video", "notes"] },
        filePath: { bsonType: "string" },
        description: { bsonType: "string" },
        createdAt: { bsonType: "date" },
        updatedAt: { bsonType: "date" }
      }
    }
  }
});

db.bTechContent.createIndex({ semesterNumber: 1 });
db.bTechContent.createIndex({ branch: 1 });

// ============================================================
// SAMPLE DOCUMENTS
// ============================================================

// Sample User Document
db.users.insertOne({
  username: "john_doe",
  email: "john@example.com",
  password: "hashed_password_here",
  firstName: "John",
  lastName: "Doe",
  phone: "+1234567890",
  profilePicture: "https://example.com/profile.jpg",
  bio: "Software developer",
  location: "San Francisco, CA",
  isActive: true,
  isStaff: false,
  isSuperuser: false,
  createdAt: new Date(),
  updatedAt: new Date()
});

// Sample Company Document
db.companies.insertOne({
  name: "TCS",
  description: "Tata Consultancy Services",
  logoUrl: "https://example.com/tcs-logo.png",
  websiteUrl: "https://www.tcs.com",
  location: "Mumbai, India",
  industry: "IT/Software",
  placementPapers: [],
  createdAt: new Date(),
  updatedAt: new Date()
});

// Sample Test Result Document
db.testResults.insertOne({
  userId: ObjectId("user_id_here"),
  testId: ObjectId("test_id_here"),
  totalQuestions: 50,
  correctAnswers: 45,
  wrongAnswers: 5,
  skippedQuestions: 0,
  score: 45,
  percentage: 90.0,
  timeSpentSeconds: 3600,
  status: "passed",
  userAnswers: [
    {
      questionId: ObjectId("question_id"),
      selectedAnswer: "Option A",
      isCorrect: true,
      timeSpent: 30
    }
  ],
  completedAt: new Date(),
  createdAt: new Date()
});

// ============================================================
// MIGRATION NOTES
// ============================================================
/*
To use this schema with MongoDB:

1. Install MongoDB (if not already installed)
2. Connect to MongoDB using the mongo shell or MongoDB Compass
3. Run this script: mongosh < schema.js

To connect from Django/Python:
- Install: pip install pymongo
- Use MongoEngine ORM for easier integration
- Or use PyMongo for direct access

Connection string format:
mongodb://username:password@localhost:27017/youtube_manage
*/
