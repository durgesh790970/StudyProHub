import sqlite3
import os
base = r'D:/All_Project/Youtube Manage/backend'
dbname = os.getenv('DJANGO_DB_NAME', 'db.sqlite3')
db = os.path.join(base, dbname)
print('DB path:', db)
con = sqlite3.connect(db)
cols = con.execute("PRAGMA table_info('accounts_pdf')").fetchall()
print('accounts_pdf columns:')
for c in cols:
    print(c)
con.close()
