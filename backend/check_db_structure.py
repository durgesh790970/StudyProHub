import sqlite3
import os

db_files = {
    'db.sqlite3': 'Django database (currently used)',
    'db.sqlite3.fixed': 'Backup - fixed version',
    'db.sqlite3.pre_recreate.bak': 'Backup - pre-recreate',
    'db.sqlite3.bak': 'Backup - original',
    'project.db': 'Custom database (NEW)',
    'accounts_pdf.db': 'PDF accounts database',
}

print('='*80)
print('DATABASE STRUCTURE ANALYSIS')
print('='*80)

for db_file, description in db_files.items():
    if os.path.exists(db_file):
        size = os.path.getsize(db_file)
        print(f'\n\n{db_file} ({size:,} bytes)')
        print(f'Description: {description}')
        print('-' * 80)
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = cursor.fetchall()
            
            if tables:
                print(f'Total Tables: {len(tables)}\n')
                for table in tables:
                    table_name = table[0]
                    cursor.execute(f"SELECT COUNT(*) FROM [{table_name}]")
                    count = cursor.fetchone()[0]
                    print(f'  • {table_name:<40} - {count:>5} records')
            else:
                print('No tables found')
            
            conn.close()
        except Exception as e:
            print(f'Error reading database: {e}')
    else:
        print(f'\n\n{db_file} - FILE NOT FOUND')

print('\n' + '='*80)
print('SUMMARY:')
print('  - db.sqlite3: Django ORM database (Settings configured here)')
print('  - accounts_pdf.db: Separate PDF-related database')
print('  - project.db: New custom database created for the setup')
print('  - Backups: db.sqlite3.fixed, db.sqlite3.bak, db.sqlite3.pre_recreate.bak')
print('='*80)
