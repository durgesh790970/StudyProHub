"""
Database Configuration Module
=============================

Centralized database configuration for the StudyPro Hub application.
Supports SQLite (development) and MongoDB (production).

Environment Variables:
    - DATABASE_TYPE: 'sqlite' or 'mongodb' (default: 'sqlite')
    - DATABASE_URL: Custom database URL
    - MONGODB_URI: MongoDB connection string
    - DATABASE_PATH: Custom SQLite database path
"""

import os
from pathlib import Path
from typing import Dict, Any

# ============================================================================
# DATABASE TYPE CONFIGURATION
# ============================================================================

DATABASE_TYPE = os.getenv('DATABASE_TYPE', 'sqlite').lower()
PROJECT_ROOT = Path(__file__).parent.parent.parent


# ============================================================================
# SQLITE CONFIGURATION
# ============================================================================

SQLITE_CONFIG = {
    'type': 'sqlite',
    'engine': 'django.db.backends.sqlite3',
    'name': os.getenv('DATABASE_PATH', str(PROJECT_ROOT / 'db.sqlite3')),
    'description': 'SQLite3 Database (Development)',
}

# ============================================================================
# MONGODB CONFIGURATION
# ============================================================================

MONGODB_CONFIG = {
    'type': 'mongodb',
    'engine': 'djongo',
    'name': 'studypro_db',
    'uri': os.getenv('MONGODB_URI', 'mongodb://localhost:27017/studypro_db'),
    'description': 'MongoDB (Production)',
    'enforce_schema_in_the_database': False,
}

# ============================================================================
# DATABASE SELECTION
# ============================================================================

def get_database_config() -> Dict[str, Any]:
    """
    Get the active database configuration based on DATABASE_TYPE.
    
    Returns:
        dict: Database configuration for Django
    """
    if DATABASE_TYPE == 'mongodb':
        return {
            'default': {
                'ENGINE': MONGODB_CONFIG['engine'],
                'NAME': MONGODB_CONFIG['name'],
                'CLIENT': {
                    'host': MONGODB_CONFIG['uri'],
                }
            }
        }
    else:
        # Default to SQLite
        return {
            'default': {
                'ENGINE': SQLITE_CONFIG['engine'],
                'NAME': SQLITE_CONFIG['name'],
            }
        }


def get_database_info() -> Dict[str, Any]:
    """Get information about the configured database."""
    if DATABASE_TYPE == 'mongodb':
        return MONGODB_CONFIG
    else:
        return SQLITE_CONFIG


# ============================================================================
# PRODUCTION SETTINGS
# ============================================================================

# For production, use environment variables
PROD_DATABASE_CONFIG = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.getenv('DB_NAME', str(PROJECT_ROOT / 'db.sqlite3')),
        'USER': os.getenv('DB_USER', ''),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', ''),
        'PORT': os.getenv('DB_PORT', ''),
    }
}

# ============================================================================
# UTILITIES
# ============================================================================

def get_db_path() -> Path:
    """Get the path to the SQLite database."""
    if DATABASE_TYPE == 'sqlite':
        return Path(SQLITE_CONFIG['name'])
    return None


def is_using_mongodb() -> bool:
    """Check if MongoDB is configured."""
    return DATABASE_TYPE.lower() == 'mongodb'


def is_using_sqlite() -> bool:
    """Check if SQLite is configured."""
    return DATABASE_TYPE.lower() != 'mongodb'


if __name__ == '__main__':
    # Print current configuration
    info = get_database_info()
    print(f"Active Database: {info['type'].upper()}")
    print(f"Description: {info['description']}")
    if 'name' in info:
        print(f"Database Name: {info['name']}")
    if 'uri' in info:
        print(f"URI: {info['uri']}")
