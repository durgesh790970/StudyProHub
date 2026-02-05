-- SQLite Database Schema for Youtube Manage Application
-- Generated: February 5, 2026
-- Database: SQLite3

-- ============================================================
-- USER MANAGEMENT TABLES
-- ============================================================

-- Users Table (extends Django's built-in User model)
CREATE TABLE IF NOT EXISTS accounts_user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    password VARCHAR(128) NOT NULL,
    last_login DATETIME,
    is_superuser BOOLEAN NOT NULL DEFAULT 0,
    username VARCHAR(150) UNIQUE NOT NULL,
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    email VARCHAR(254) UNIQUE NOT NULL,
    is_staff BOOLEAN NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    date_joined DATETIME NOT NULL,
    -- Custom fields for the application
    phone VARCHAR(20),
    profile_picture VARCHAR(100),
    bio TEXT,
    location VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- MOCK TEST & INTERVIEW TABLES
-- ============================================================

-- Mock Test/Interview Sessions
CREATE TABLE IF NOT EXISTS accounts_mocktest (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    duration_minutes INTEGER,
    difficulty_level VARCHAR(50), -- easy, medium, hard
    category VARCHAR(100), -- technical, HR, aptitude
    start_time DATETIME,
    end_time DATETIME,
    score INTEGER,
    max_score INTEGER,
    status VARCHAR(50), -- not_started, in_progress, completed
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES accounts_user(id)
);

-- ============================================================
-- QUESTIONS & ANSWERS TABLES
-- ============================================================

-- Questions Table
CREATE TABLE IF NOT EXISTS accounts_question (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    category VARCHAR(100), -- technical, HR, aptitude, interview
    difficulty_level VARCHAR(50), -- easy, medium, hard
    question_type VARCHAR(50), -- multiple_choice, essay, coding
    marks INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Test Results Table
CREATE TABLE IF NOT EXISTS accounts_testresult (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    test_id INTEGER,
    total_questions INTEGER,
    correct_answers INTEGER,
    wrong_answers INTEGER,
    skipped_questions INTEGER,
    score FLOAT,
    percentage FLOAT,
    time_taken_seconds INTEGER,
    status VARCHAR(50), -- passed, failed
    completed_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES accounts_user(id),
    FOREIGN KEY (test_id) REFERENCES accounts_mocktest(id)
);

-- User Answers/Responses
CREATE TABLE IF NOT EXISTS accounts_useranswer (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    test_result_id INTEGER,
    selected_answer TEXT,
    is_correct BOOLEAN,
    time_spent_seconds INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES accounts_user(id),
    FOREIGN KEY (question_id) REFERENCES accounts_question(id),
    FOREIGN KEY (test_result_id) REFERENCES accounts_testresult(id)
);

-- ============================================================
-- PAYMENT & TRANSACTION TABLES
-- ============================================================

-- Transactions Table
CREATE TABLE IF NOT EXISTS accounts_transaction (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'USD',
    transaction_type VARCHAR(50), -- payment, refund, subscription
    payment_method VARCHAR(50), -- credit_card, debit_card, paypal, etc.
    status VARCHAR(50), -- pending, completed, failed, cancelled
    reference_id VARCHAR(255) UNIQUE,
    description TEXT,
    receipt_url VARCHAR(500),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES accounts_user(id)
);

-- ============================================================
-- COURSE & CONTENT TABLES
-- ============================================================

-- B.Tech Semesters Content
CREATE TABLE IF NOT EXISTS accounts_semester (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    semester_number INTEGER NOT NULL,
    branch VARCHAR(100), -- CSE, ECE, EEE, etc.
    subject_name VARCHAR(255) NOT NULL,
    content_type VARCHAR(50), -- pdf, video, notes
    file_path VARCHAR(500),
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- COMPANY & JOB RELATED TABLES
-- ============================================================

-- Companies
CREATE TABLE IF NOT EXISTS accounts_company (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    logo_url VARCHAR(500),
    website_url VARCHAR(500),
    location VARCHAR(255),
    industry VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Company Placement Papers
CREATE TABLE IF NOT EXISTS accounts_placementpaper (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    year INTEGER,
    semester VARCHAR(50),
    pdf_url VARCHAR(500),
    difficulty_level VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES accounts_company(id)
);

-- Job Applications
CREATE TABLE IF NOT EXISTS accounts_jobapplication (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    company_id INTEGER NOT NULL,
    job_title VARCHAR(255),
    salary_offered DECIMAL(10, 2),
    status VARCHAR(50), -- applied, rejected, offered, accepted
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    response_date DATETIME,
    FOREIGN KEY (user_id) REFERENCES accounts_user(id),
    FOREIGN KEY (company_id) REFERENCES accounts_company(id)
);

-- ============================================================
-- INTERVIEW SESSION TABLES
-- ============================================================

-- Interview Sessions (Mock/Actual)
CREATE TABLE IF NOT EXISTS accounts_interviewsession (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    company_id INTEGER,
    session_type VARCHAR(50), -- technical, hr, coding
    duration_minutes INTEGER,
    feedback TEXT,
    rating INTEGER, -- 1-5 stars
    scheduled_at DATETIME,
    started_at DATETIME,
    ended_at DATETIME,
    recording_url VARCHAR(500),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES accounts_user(id),
    FOREIGN KEY (company_id) REFERENCES accounts_company(id)
);

-- ============================================================
-- FEEDBACK & RATINGS TABLES
-- ============================================================

-- User Feedback
CREATE TABLE IF NOT EXISTS accounts_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    feedback_type VARCHAR(50), -- bug_report, feature_request, general
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    rating INTEGER, -- 1-5 stars
    status VARCHAR(50), -- pending, reviewed, resolved
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES accounts_user(id)
);

-- ============================================================
-- SUBSCRIPTION & ITEMS TABLES
-- ============================================================

-- Items/Products (for purchases)
CREATE TABLE IF NOT EXISTS accounts_item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    item_type VARCHAR(50), -- course, test_pack, premium_membership
    quantity_available INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- User Item Purchases
CREATE TABLE IF NOT EXISTS accounts_userpurchase (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    transaction_id INTEGER,
    quantity INTEGER DEFAULT 1,
    purchase_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    expiry_date DATETIME,
    FOREIGN KEY (user_id) REFERENCES accounts_user(id),
    FOREIGN KEY (item_id) REFERENCES accounts_item(id),
    FOREIGN KEY (transaction_id) REFERENCES accounts_transaction(id)
);

-- ============================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================

-- User related indexes
CREATE INDEX IF NOT EXISTS idx_user_email ON accounts_user(email);
CREATE INDEX IF NOT EXISTS idx_user_username ON accounts_user(username);
CREATE INDEX IF NOT EXISTS idx_user_active ON accounts_user(is_active);

-- Test related indexes
CREATE INDEX IF NOT EXISTS idx_mocktest_user ON accounts_mocktest(user_id);
CREATE INDEX IF NOT EXISTS idx_mocktest_status ON accounts_mocktest(status);
CREATE INDEX IF NOT EXISTS idx_testresult_user ON accounts_testresult(user_id);
CREATE INDEX IF NOT EXISTS idx_testresult_test ON accounts_testresult(test_id);

-- Transaction related indexes
CREATE INDEX IF NOT EXISTS idx_transaction_user ON accounts_transaction(user_id);
CREATE INDEX IF NOT EXISTS idx_transaction_status ON accounts_transaction(status);
CREATE INDEX IF NOT EXISTS idx_transaction_reference ON accounts_transaction(reference_id);

-- Interview related indexes
CREATE INDEX IF NOT EXISTS idx_interview_user ON accounts_interviewsession(user_id);
CREATE INDEX IF NOT EXISTS idx_interview_company ON accounts_interviewsession(company_id);

-- Placement related indexes
CREATE INDEX IF NOT EXISTS idx_placement_company ON accounts_placementpaper(company_id);
CREATE INDEX IF NOT EXISTS idx_job_application_user ON accounts_jobapplication(user_id);

-- Question related indexes
CREATE INDEX IF NOT EXISTS idx_question_category ON accounts_question(category);
CREATE INDEX IF NOT EXISTS idx_question_difficulty ON accounts_question(difficulty_level);

-- ============================================================
-- VIEWS (Optional - for common queries)
-- ============================================================

-- User Performance Summary
CREATE VIEW IF NOT EXISTS user_performance_summary AS
SELECT 
    u.id,
    u.username,
    u.email,
    COUNT(DISTINCT tr.id) as total_tests,
    AVG(tr.percentage) as avg_score,
    MAX(tr.percentage) as best_score,
    COUNT(CASE WHEN tr.status = 'passed' THEN 1 END) as passed_tests,
    COUNT(CASE WHEN tr.status = 'failed' THEN 1 END) as failed_tests
FROM accounts_user u
LEFT JOIN accounts_testresult tr ON u.id = tr.user_id
GROUP BY u.id;

-- Transaction Summary by User
CREATE VIEW IF NOT EXISTS user_transaction_summary AS
SELECT 
    u.id,
    u.username,
    COUNT(t.id) as total_transactions,
    SUM(CASE WHEN t.status = 'completed' THEN t.amount ELSE 0 END) as total_spent,
    COUNT(CASE WHEN t.status = 'completed' THEN 1 END) as successful_payments
FROM accounts_user u
LEFT JOIN accounts_transaction t ON u.id = t.user_id
GROUP BY u.id;

-- ============================================================
-- TABLE COMMENTS (SQLite doesn't support comments directly)
-- ============================================================
-- This schema supports:
-- 1. User Management (authentication, profiles)
-- 2. Mock Tests & Interviews (practice and tracking)
-- 3. Questions & Answers (quiz system)
-- 4. Test Results (performance tracking)
-- 5. Payments & Transactions (payment processing)
-- 6. B.Tech Content (course materials)
-- 7. Company & Placement Data (job preparation)
-- 8. Interview Sessions (interview tracking)
-- 9. Feedback System (user feedback)
-- 10. Subscriptions & Items (product management)

-- Version: 1.0.0
-- Last Updated: February 5, 2026
