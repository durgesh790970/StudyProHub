import sqlite3
db = r'D:/All_Project/Youtube Manage/backend/db.sqlite3'
con=sqlite3.connect(db)
cur=con.cursor()
cols=cur.execute("PRAGMA table_info('accounts_pdf')").fetchall()
print('accounts_pdf columns:')
for c in cols:
    print(c)
con.close()
