import csv
import psycopg2

# Connect to PostgreSQL
cur = conn.cursor()

# Create table if it doesn't exist
cur.execute("""
    CREATE TABLE IF NOT EXISTS cities (
        id SERIAL PRIMARY KEY,
        name TEXT,
        age INTEGER,
        email TEXT
    );
""")
conn.commit()

# Read CSV and insert rows
with open('cities.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        cur.execute(
            "INSERT INTO cities (City, State, EW) VALUES (%s, %s, %s)",
            (row['City'], row['State'], row['EW'])
        )
conn.commit()
cur.close()
conn.close()
print("CSV data inserted into database.")