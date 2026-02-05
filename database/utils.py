"""
Database Utilities Module
=========================

Helper functions for database operations, migrations, and maintenance.

Functions:
    - Database backup/restore
    - Table operations
    - Data seeding
    - Connection validation
"""

import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# BACKUP & RESTORE
# ============================================================================

def backup_database(db_path: Path, backup_dir: Optional[Path] = None) -> bool:
    """
    Create a backup of the SQLite database.
    
    Args:
        db_path: Path to the database file
        backup_dir: Directory to store backup (defaults to db parent directory)
    
    Returns:
        bool: True if successful
    """
    try:
        if not db_path.exists():
            logger.error(f"Database file not found: {db_path}")
            return False
        
        backup_dir = backup_dir or db_path.parent / 'backups'
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = backup_dir / f"db_backup_{timestamp}.sqlite3"
        
        # Use SQLite backup mechanism
        conn = sqlite3.connect(str(db_path))
        backup_conn = sqlite3.connect(str(backup_file))
        
        with backup_conn:
            conn.backup(backup_conn)
        
        conn.close()
        backup_conn.close()
        
        logger.info(f"✅ Database backed up to {backup_file}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Backup failed: {e}")
        return False


def restore_database(db_path: Path, backup_file: Path) -> bool:
    """
    Restore database from a backup file.
    
    Args:
        db_path: Path to the target database file
        backup_file: Path to the backup file
    
    Returns:
        bool: True if successful
    """
    try:
        if not backup_file.exists():
            logger.error(f"Backup file not found: {backup_file}")
            return False
        
        # Backup current database before restore
        if db_path.exists():
            backup_database(db_path)
        
        # Restore from backup
        conn = sqlite3.connect(str(backup_file))
        restore_conn = sqlite3.connect(str(db_path))
        
        with restore_conn:
            conn.backup(restore_conn)
        
        conn.close()
        restore_conn.close()
        
        logger.info(f"✅ Database restored from {backup_file}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Restore failed: {e}")
        return False


# ============================================================================
# TABLE OPERATIONS
# ============================================================================

def get_tables(db_path: Path) -> List[str]:
    """
    Get list of all tables in the database.
    
    Args:
        db_path: Path to the database file
    
    Returns:
        list: Table names
    """
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return tables
        
    except Exception as e:
        logger.error(f"Failed to get tables: {e}")
        return []


def get_table_schema(db_path: Path, table_name: str) -> str:
    """
    Get the SQL schema for a specific table.
    
    Args:
        db_path: Path to the database file
        table_name: Name of the table
    
    Returns:
        str: SQL schema
    """
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        result = cursor.fetchone()
        
        conn.close()
        return result[0] if result else None
        
    except Exception as e:
        logger.error(f"Failed to get schema for {table_name}: {e}")
        return None


def get_row_count(db_path: Path, table_name: str) -> int:
    """
    Get the number of rows in a table.
    
    Args:
        db_path: Path to the database file
        table_name: Name of the table
    
    Returns:
        int: Number of rows
    """
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        
        conn.close()
        return count
        
    except Exception as e:
        logger.error(f"Failed to get row count for {table_name}: {e}")
        return 0


def get_database_stats(db_path: Path) -> Dict[str, Any]:
    """
    Get statistics about the database.
    
    Args:
        db_path: Path to the database file
    
    Returns:
        dict: Database statistics
    """
    if not db_path.exists():
        return {'error': 'Database file not found'}
    
    tables = get_tables(db_path)
    stats = {
        'file_path': str(db_path),
        'file_size_kb': db_path.stat().st_size / 1024,
        'table_count': len(tables),
        'tables': {}
    }
    
    for table in tables:
        stats['tables'][table] = {
            'row_count': get_row_count(db_path, table),
            'schema': get_table_schema(db_path, table)
        }
    
    return stats


# ============================================================================
# DATA EXPORT
# ============================================================================

def export_table_to_json(db_path: Path, table_name: str, output_file: Path) -> bool:
    """
    Export a table to JSON format.
    
    Args:
        db_path: Path to the database file
        table_name: Name of the table
        output_file: Path to the output JSON file
    
    Returns:
        bool: True if successful
    """
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        data = [dict(row) for row in rows]
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        
        conn.close()
        logger.info(f"✅ Table {table_name} exported to {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Export failed: {e}")
        return False


def export_all_tables_to_json(db_path: Path, output_dir: Path) -> bool:
    """
    Export all tables to JSON files.
    
    Args:
        db_path: Path to the database file
        output_dir: Directory to store JSON files
    
    Returns:
        bool: True if successful
    """
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        tables = get_tables(db_path)
        
        for table in tables:
            output_file = output_dir / f"{table}.json"
            export_table_to_json(db_path, table, output_file)
        
        logger.info(f"✅ All tables exported to {output_dir}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Export all failed: {e}")
        return False


if __name__ == '__main__':
    # Example usage
    from database.init_db import get_db_path
    
    db_path = get_db_path()
    if db_path and db_path.exists():
        stats = get_database_stats(db_path)
        print(json.dumps(stats, indent=2))
