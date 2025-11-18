#!/usr/bin/env python3
"""
Initialize the database for Astavaisya rental bot
"""
import sys
import os

# Add bot directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bot'))

from database import init_db, get_connection

def main():
    print("Initializing database...")
    init_db()
    print("Database initialized successfully!")

    # Show some stats
    conn = get_connection()

    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()

    print(f"\nCreated {len(tables)} tables:")
    for table in tables:
        count = conn.execute(f"SELECT COUNT(*) FROM {table['name']}").fetchone()[0]
        print(f"  - {table['name']}: {count} records")

    conn.close()
    print("\nDatabase is ready to use!")
    print("Default admin: admin / admin123")

if __name__ == "__main__":
    main()
