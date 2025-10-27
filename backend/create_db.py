import sqlite3

# Global variable for table name
TABLE_NAME = "pois"

# Local variable for data
sample_data = [
    ("Starbucks", "New York", 1200),
    ("Target", "San Francisco", 900),
    ("McDonald's", "Los Angeles", 700),
]

# Connect to (or create) the database
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Create table if not exists
cursor.execute(f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    city TEXT,
    visits INTEGER
)
""")

# Insert sample data
cursor.executemany(
    f"INSERT INTO {TABLE_NAME} (name, city, visits) VALUES (?, ?, ?)",
    sample_data
)

conn.commit()
conn.close()
print(f"Database created with sample data in table '{TABLE_NAME}'.")
