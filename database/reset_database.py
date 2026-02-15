#!/usr/bin/env python3
"""
Reset database - removes old DB and creates fresh one with new schema
"""

import sqlite3
import os
from pathlib import Path

DB_PATH = Path(__file__).parent / 'rental.db'
SCHEMA_PATH = Path(__file__).parent / 'schema.sql'

def main():
    print("="*60)
    print("DATABASE RESET")
    print("="*60)

    print("\n⚠️  WARNING: This will delete the current database!")
    print(f"Database path: {DB_PATH}")

    # Check if DB exists
    if DB_PATH.exists():
        print(f"\nCurrent database size: {DB_PATH.stat().st_size / 1024:.2f} KB")
        response = input("\nDo you want to continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Operation cancelled")
            return

        # Remove old database
        print("\n1. Removing old database...")
        os.remove(DB_PATH)
        print("   ✓ Old database removed")
    else:
        print("\nNo existing database found")

    # Create new database with schema
    print("\n2. Creating new database with updated schema...")

    if not SCHEMA_PATH.exists():
        print(f"   ✗ Error: Schema file not found at {SCHEMA_PATH}")
        return

    # Read schema
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        schema = f.read()

    # Create new database
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(schema)
    conn.commit()

    # Verify tables
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]

    print(f"   ✓ Database created with {len(tables)} tables:")
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"      - {table}: {count} records")

    conn.close()

    print("\n" + "="*60)
    print("✅ Database reset completed!")
    print("="*60)
    print("\nNext step: Run 'python3 init_database.py' to populate with data")

if __name__ == "__main__":
    main()
