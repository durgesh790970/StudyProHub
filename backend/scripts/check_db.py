import os, sys
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE','djproject.settings')
import django
django.setup()
from django.conf import settings
import sqlite3, pathlib
print('Django DB setting:', settings.DATABASES['default']['NAME'])
db = str(settings.DATABASES['default']['NAME'])
print('DB exists:', pathlib.Path(db).exists())
if pathlib.Path(db).exists():
    con = sqlite3.connect(db)
    cur = con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = cur.fetchall()
    print('Tables in DB:')
    for t in tables:
        print(' -', t[0])
    con.close()
    # show applied migrations for 'accounts'
    con = sqlite3.connect(db)
    cur = con.cursor()
    try:
        cur.execute("SELECT name, app FROM django_migrations WHERE app='accounts' ORDER BY name;")
        rows = cur.fetchall()
        print('\nApplied migrations recorded for app "accounts":')
        for r in rows:
            print(' -', r[0])
    except Exception as e:
        print('Could not query django_migrations:', e)
    finally:
        con.close()
else:
    print('No DB file found at that path')
