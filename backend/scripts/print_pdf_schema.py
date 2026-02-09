import sqlite3
con=sqlite3.connect('db.sqlite3')
cur=con.cursor()
cols=cur.execute("PRAGMA table_info('accounts_pdf')").fetchall()
print('accounts_pdf columns:')
for c in cols:
    print(c)
con.close()
