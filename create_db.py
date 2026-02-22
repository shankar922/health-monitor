import sqlite3

# connect to database file
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# create users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    password TEXT
)
""")

# create health table
cursor.execute("""
CREATE TABLE IF NOT EXISTS health (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    heart_rate INTEGER,
    bp INTEGER,
    sugar INTEGER,
    risk TEXT
)
""")

conn.commit()
conn.close()

print("Database and tables created successfully")
