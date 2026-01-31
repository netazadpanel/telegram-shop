import sqlite3

conn = sqlite3.connect("store.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS single_products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_url TEXT,
    download_link TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS multi_products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_url TEXT,
    download_link TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    category TEXT,
    product_id INTEGER,
    status TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS sales_report (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    category TEXT,
    sold_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()

print("Database created successfully!")
