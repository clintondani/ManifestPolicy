# init_db_run.py
from db import init_db

init_db()
#print("✅ Database and table initialized successfully.")

import sqlite3

conn = sqlite3.connect("scanner.db")
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(scans)")
print(cursor.fetchall())
conn.close()
