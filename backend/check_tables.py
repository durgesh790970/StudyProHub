#!/usr/bin/env python
import sqlite3

conn = sqlite3.connect('database/app.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('Existing Tables:')
for t in tables:
    print(f'  - {t[0]}')

conn.close()
