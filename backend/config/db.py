"""
Database Connection Module
===========================

SQLite database connection, initialization, and management.
Handles schema creation, migrations, and database operations.

Database File: backend/database/app.db
Type: SQLite3
"""

import sqlite3
import os
from pathlib import Path
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

# Get project directories
BACKEND_DIR = Path(__file__).parent.parent
DATABASE_DIR = BACKEND_DIR / 'database'
DB_PATH = DATABASE_DIR / 'app.db'

# Create database directory if it doesn't exist
DATABASE_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# DATABASE CONNECTION
# ============================================================================

def get_db_connection():
    """
    Get a SQLite database connection.
    
    Returns:
        sqlite3.Connection: Database connection object
    """
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row  # Allow accessing columns by name
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        raise


def close_db_connection(conn):
    """Close database connection."""
    if conn:
        conn.close()
        logger.info("Database connection closed")


# ============================================================================
# SCHEMA DEFINITION
# ============================================================================

SCHEMA = """
-- ====================================================================
-- USERS TABLE
-- ====================================================================
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    role VARCHAR(50) DEFAULT 'user' CHECK(role IN ('admin', 'user')),
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Index on email for faster authentication
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- ====================================================================
-- USER PROFILES TABLE
-- ====================================================================
CREATE TABLE IF NOT EXISTS user_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    address VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(100),
    pincode VARCHAR(10),
    date_of_birth DATE,
    gender VARCHAR(20),
    profile_image VARCHAR(255),
    bio TEXT,
    phone_verified BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Index for quick profile lookup
CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id);

-- ====================================================================
-- TRANSACTIONS TABLE
-- ====================================================================
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    transaction_id VARCHAR(255) UNIQUE NOT NULL,
    status VARCHAR(50) DEFAULT 'pending' CHECK(status IN ('pending', 'success', 'failed', 'refunded')),
    description TEXT,
    currency VARCHAR(10) DEFAULT 'INR',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Indexes for transaction queries
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status);
CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON transactions(created_at);

-- ====================================================================
-- ACTIVITY LOGS TABLE
-- ====================================================================
CREATE TABLE IF NOT EXISTS activity_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    activity VARCHAR(255) NOT NULL,
    activity_type VARCHAR(50),
    ip_address VARCHAR(45),
    user_agent TEXT,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Indexes for activity queries
CREATE INDEX IF NOT EXISTS idx_activity_logs_user_id ON activity_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_logs_created_at ON activity_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_activity_logs_activity_type ON activity_logs(activity_type);

-- ====================================================================
-- SESSIONS TABLE (for token management)
-- ====================================================================
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token VARCHAR(255) UNIQUE NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Indexes for session queries
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(token);

-- ====================================================================
-- AUDIT LOGS TABLE (for compliance)
-- ====================================================================
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action VARCHAR(100) NOT NULL,
    table_name VARCHAR(100),
    record_id INTEGER,
    old_values TEXT,
    new_values TEXT,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Indexes for audit queries
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_table_name ON audit_logs(table_name);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);

-- ====================================================================
-- SETTINGS TABLE (for app configuration)
-- ====================================================================
CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key VARCHAR(255) UNIQUE NOT NULL,
    value TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ====================================================================
-- VERIFY DATABASE IS READY
-- ====================================================================
-- Database schema is now ready for use
"""

# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def initialize_database():
    """
    Initialize the database by creating all tables and indexes.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Execute schema
        cursor.executescript(SCHEMA)
        conn.commit()
        
        logger.info(f"✅ Database initialized at {DB_PATH}")
        logger.info("✅ All tables and indexes created")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        logger.error(f"❌ Database initialization error: {e}")
        return False


def drop_all_tables():
    """
    Drop all tables (use with caution - development only).
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        tables = [
            'audit_logs',
            'sessions',
            'activity_logs',
            'transactions',
            'user_profiles',
            'users',
            'settings'
        ]
        
        for table in tables:
            cursor.execute(f"DROP TABLE IF EXISTS {table}")
        
        conn.commit()
        logger.info("✅ All tables dropped")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        logger.error(f"❌ Error dropping tables: {e}")
        return False


def reset_database():
    """
    Reset database (drop all tables and recreate).
    
    Returns:
        bool: True if successful, False otherwise
    """
    if drop_all_tables():
        return initialize_database()
    return False


# ============================================================================
# DATABASE INFO & STATUS
# ============================================================================

def get_database_info():
    """
    Get information about the database.
    
    Returns:
        dict: Database information
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get table info
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = [row[0] for row in cursor.fetchall()]
        
        # Get record counts
        table_info = {}
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            table_info[table] = count
        
        # Get database file size
        file_size = os.path.getsize(DB_PATH) / 1024  # Size in KB
        
        info = {
            'database': str(DB_PATH),
            'type': 'SQLite3',
            'file_size_kb': round(file_size, 2),
            'tables': tables,
            'table_records': table_info,
            'total_records': sum(table_info.values())
        }
        
        conn.close()
        return info
        
    except Exception as e:
        logger.error(f"Error getting database info: {e}")
        return {}


def verify_database():
    """
    Verify database integrity and connectivity.
    
    Returns:
        bool: True if database is healthy, False otherwise
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if main tables exist
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
        )
        if not cursor.fetchone():
            logger.error("❌ Database not initialized")
            conn.close()
            return False
        
        # Run PRAGMA check
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()[0]
        
        conn.close()
        
        if result == 'ok':
            logger.info("✅ Database integrity verified")
            return True
        else:
            logger.error(f"❌ Database integrity check failed: {result}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Database verification error: {e}")
        return False


# ============================================================================
# DATABASE OPERATIONS
# ============================================================================

def execute_query(query, params=None, fetch_one=False):
    """
    Execute a database query.
    
    Args:
        query (str): SQL query to execute
        params (tuple): Query parameters for parameterized queries
        fetch_one (bool): If True, returns single row; if False, returns all rows
    
    Returns:
        dict/list/int: Query result or affected row count
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        conn.commit()
        
        if fetch_one:
            result = cursor.fetchone()
        else:
            result = cursor.fetchall()
        
        conn.close()
        return result if result is not None else 0
        
    except sqlite3.Error as e:
        logger.error(f"Query execution error: {e}")
        return None


def get_record_by_id(table, record_id):
    """Get a single record by ID."""
    query = f"SELECT * FROM {table} WHERE id = ?"
    return execute_query(query, (record_id,), fetch_one=True)


def get_all_records(table, limit=None):
    """Get all records from a table."""
    query = f"SELECT * FROM {table}"
    if limit:
        query += f" LIMIT {limit}"
    return execute_query(query)


def insert_record(table, data):
    """
    Insert a record into a table.
    
    Args:
        table (str): Table name
        data (dict): Column names and values
    
    Returns:
        int: ID of inserted record or 0 on failure
    """
    columns = ', '.join(data.keys())
    placeholders = ', '.join(['?' for _ in data])
    query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, tuple(data.values()))
        conn.commit()
        
        last_id = cursor.lastrowid
        conn.close()
        
        return last_id
        
    except sqlite3.Error as e:
        logger.error(f"Insert error: {e}")
        return 0


def update_record(table, record_id, data):
    """
    Update a record in a table.
    
    Args:
        table (str): Table name
        record_id (int): Record ID to update
        data (dict): Column names and new values
    
    Returns:
        bool: True if successful, False otherwise
    """
    set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
    query = f"UPDATE {table} SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, (*data.values(), record_id))
        conn.commit()
        
        success = cursor.rowcount > 0
        conn.close()
        
        return success
        
    except sqlite3.Error as e:
        logger.error(f"Update error: {e}")
        return False


def delete_record(table, record_id):
    """
    Delete a record from a table.
    
    Args:
        table (str): Table name
        record_id (int): Record ID to delete
    
    Returns:
        bool: True if successful, False otherwise
    """
    query = f"DELETE FROM {table} WHERE id = ?"
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, (record_id,))
        conn.commit()
        
        success = cursor.rowcount > 0
        conn.close()
        
        return success
        
    except sqlite3.Error as e:
        logger.error(f"Delete error: {e}")
        return False


# ============================================================================
# INITIALIZATION ON IMPORT
# ============================================================================

if __name__ == '__main__':
    print("Initializing database...")
    if initialize_database():
        print("✅ Database ready!")
        info = get_database_info()
        print(f"\nDatabase Info:")
        print(f"  Path: {info['database']}")
        print(f"  Size: {info['file_size_kb']} KB")
        print(f"  Tables: {len(info['tables'])}")
    else:
        print("❌ Database initialization failed")
