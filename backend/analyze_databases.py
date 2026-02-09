#!/usr/bin/env python
"""Analyze all SQLite database files in the project"""

import sqlite3
import os

db_files = ['db.sqlite3', 'project.db', 'accounts_pdf.db']

print('='*70)
print('DATABASE FILES ANALYSIS')
print('='*70)

for db_file in db_files:
    if os.path.exists(db_file):
        size = os.path.getsize(db_file)
        print(f'\n{db_file} (Size: {size} bytes)')
        print('-' * 70)
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f'Tables: {len(tables)}')
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM [{table[0]}]")
                count = cursor.fetchone()[0]
                print(f'   - {table[0]}: {count} records')
            conn.close()
        except Exception as e:
            print(f'Error: {e}')
    else:
        print(f'\nNOT FOUND: {db_file}')

print('\n' + '='*70)
