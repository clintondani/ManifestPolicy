import sqlite3

conn = sqlite3.connect("scanner.db")
cursor = conn.cursor()

cursor.execute("""
ALTER TABLE scans
ADD COLUMN summary TEXT
""")

conn.commit()
conn.close()

print("✅ 'summary' column added successfully")
