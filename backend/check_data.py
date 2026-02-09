#!/usr/bin/env python
import sqlite3
from pathlib import Path

db_path = Path.cwd() / 'database' / 'app.db'
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Count users
cursor.execute('SELECT COUNT(*) FROM users')
count = cursor.fetchone()[0]
print(f'Total users in database: {count}')

# Show sample users
if count > 0:
    cursor.execute('SELECT email, first_name, created_at FROM users LIMIT 5')
    rows = cursor.fetchall()
    print(f'\nSample users:')
    for row in rows:
        print(f'  - {row[0]} ({row[1]}) - Created: {row[2]}')

# Check profiles
cursor.execute('SELECT COUNT(*) FROM user_profiles')
profile_count = cursor.fetchone()[0]
print(f'\nUser profiles: {profile_count}')

# Check transactions
cursor.execute('SELECT COUNT(*) FROM transactions')
tx_count = cursor.fetchone()[0]
print(f'Transactions: {tx_count}')

# Check test results
cursor.execute('SELECT COUNT(*) FROM test_results')
test_count = cursor.fetchone()[0]
print(f'Test results: {test_count}')

conn.close()
print('\n✓ Database verification complete')
