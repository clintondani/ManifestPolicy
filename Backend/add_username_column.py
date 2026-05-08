import sqlite3

conn = sqlite3.connect("scanner.db")
cursor = conn.cursor()
cursor.execute("ALTER TABLE scans ADD COLUMN username TEXT")
conn.commit()
conn.close()

print("✅ Added 'username' column successfully.")
