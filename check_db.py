import sqlite3

conn = sqlite3.connect('./jaegis_nexus_sync.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print("Tables:", tables)

# Check if there's a config table
if 'config' in tables or 'settings' in tables:
    table_name = 'config' if 'config' in tables else 'settings'
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    print(f"\n{table_name} table:")
    for row in rows:
        print(row)

conn.close()

