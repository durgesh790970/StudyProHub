"""
Database Initialization Module
==============================

This module handles database initialization, schema creation, and connection management
for the StudyPro Hub application.

Features:
- SQLite database setup for development
- MongoDB connection for production (optional)
- Schema validation
- Database seeding with initial data

Usage:
    from database.init_db import initialize_database, get_db_path
    
    # Initialize database on application startup
    initialize_database()
    
    # Get database path
    db_path = get_db_path()
"""

import os
import sqlite3
from pathlib import Path
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

# Get the backend directory path
BACKEND_DIR = Path(__file__).parent.parent
PROJECT_ROOT = BACKEND_DIR.parent
DATABASE_DIR = BACKEND_DIR / 'database'

# SQLite database file location
SQLITE_DB_PATH = PROJECT_ROOT / 'db.sqlite3'

# ============================================================================
# DATABASE PATH UTILITY
# ============================================================================

def get_db_path() -> Path:
    """Get the path to the SQLite database file."""
    return SQLITE_DB_PATH


def get_db_url() -> str:
    """Get the database URL for connections."""
    return f'sqlite:///{SQLITE_DB_PATH}'


# ============================================================================
# SQLite INITIALIZATION
# ============================================================================

def load_schema() -> str:
    """Load SQL schema from schema.sql file."""
    schema_file = DATABASE_DIR / 'schema.sql'
    
    if not schema_file.exists():
        logger.warning(f"Schema file not found at {schema_file}")
        return ""
    
    with open(schema_file, 'r', encoding='utf-8') as f:
        return f.read()


def initialize_sqlite_database() -> bool:
    """
    Initialize SQLite database with schema.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create database connection
        conn = sqlite3.connect(str(SQLITE_DB_PATH))
        cursor = conn.cursor()
        
        # Load and execute schema
        schema = load_schema()
        if schema:
            # Split by ; and execute each statement
            statements = [stmt.strip() for stmt in schema.split(';') if stmt.strip()]
            for statement in statements:
                cursor.execute(statement)
            
            conn.commit()
            logger.info(f"✅ SQLite database initialized at {SQLITE_DB_PATH}")
        
        conn.close()
        return True
        
    except sqlite3.DatabaseError as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error during database initialization: {e}")
        return False


# ============================================================================
# MONGODB INITIALIZATION (Optional)
# ============================================================================

def initialize_mongodb() -> bool:
    """
    Initialize MongoDB connection (optional for production).
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        import pymongo
        
        # Get MongoDB URI from environment or use local
        mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
        client = pymongo.MongoClient(mongo_uri)
        
        # Test connection
        client.admin.command('ping')
        logger.info(f"✅ MongoDB connection established: {mongo_uri}")
        
        return True
        
    except ImportError:
        logger.info("⚠️  PyMongo not installed. MongoDB support unavailable.")
        return False
    except Exception as e:
        logger.error(f"❌ MongoDB initialization failed: {e}")
        return False


# ============================================================================
# MAIN INITIALIZATION
# ============================================================================

def initialize_database(use_mongodb: bool = False) -> bool:
    """
    Initialize the database based on configuration.
    
    Args:
        use_mongodb (bool): If True, initialize MongoDB. Otherwise use SQLite.
    
    Returns:
        bool: True if successful, False otherwise
    """
    
    # Check if database directory exists
    if not DATABASE_DIR.exists():
        DATABASE_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created database directory: {DATABASE_DIR}")
    
    # Initialize based on preference
    if use_mongodb:
        return initialize_mongodb()
    else:
        return initialize_sqlite_database()


def database_exists() -> bool:
    """Check if database file exists."""
    return SQLITE_DB_PATH.exists()


def reset_database() -> bool:
    """
    Reset (delete and recreate) the database.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if SQLITE_DB_PATH.exists():
            SQLITE_DB_PATH.unlink()
            logger.info(f"Deleted existing database: {SQLITE_DB_PATH}")
        
        return initialize_database()
        
    except Exception as e:
        logger.error(f"❌ Database reset failed: {e}")
        return False


# ============================================================================
# VERIFICATION
# ============================================================================

def verify_database() -> bool:
    """
    Verify database integrity and connectivity.
    
    Returns:
        bool: True if database is healthy, False otherwise
    """
    try:
        if not database_exists():
            logger.warning("Database file does not exist")
            return False
        
        conn = sqlite3.connect(str(SQLITE_DB_PATH))
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        if not tables:
            logger.warning("Database exists but has no tables")
            conn.close()
            return False
        
        logger.info(f"✅ Database verified. Found {len(tables)} tables")
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Database verification failed: {e}")
        return False


if __name__ == '__main__':
    # Example usage
    print("Initializing database...")
    success = initialize_database()
    
    if success:
        print("Verifying database...")
        if verify_database():
            print("✅ Database setup complete!")
        else:
            print("⚠️  Database verification failed")
    else:
        print("❌ Database initialization failed")
