import sqlite3

conn = sqlite3.connect("data/app.db")
cur = conn.cursor()

cur.execute("SELECT link, joined_at, account_phone FROM groups;")
rows = cur.fetchall()

for row in rows:
    print(f"Group: {row[0]}, Joined at: {row[1]}, Account: {row[2]}")
