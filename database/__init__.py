"""
Database Package
================

Database initialization, configuration, and utilities for StudyPro Hub.

Modules:
    - init_db: Database initialization and schema setup
    - config: Database configuration management
    - utils: Database utilities (backup, restore, export, etc.)

Quick Start:
    from database import initialize_database, get_db_path
    
    # Initialize database
    initialize_database()
    
    # Get database path
    db_path = get_db_path()
"""

from .init_db import (
    initialize_database,
    database_exists,
    verify_database,
    get_db_path,
    get_db_url,
    reset_database,
)

from .config import (
    get_database_config,
    get_database_info,
    is_using_mongodb,
    is_using_sqlite,
)

from .utils import (
    backup_database,
    restore_database,
    get_tables,
    get_table_schema,
    get_row_count,
    get_database_stats,
    export_table_to_json,
    export_all_tables_to_json,
)

__all__ = [
    # Initialization
    'initialize_database',
    'database_exists',
    'verify_database',
    'reset_database',
    'get_db_path',
    'get_db_url',
    
    # Configuration
    'get_database_config',
    'get_database_info',
    'is_using_mongodb',
    'is_using_sqlite',
    
    # Utilities
    'backup_database',
    'restore_database',
    'get_tables',
    'get_table_schema',
    'get_row_count',
    'get_database_stats',
    'export_table_to_json',
    'export_all_tables_to_json',
]

__version__ = '1.0.0'
