#!/usr/bin/env python3
"""Clean up database - remove unnecessary cities and districts"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / 'database' / 'rental.db'

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("=== Available Tables ===")
    for table in tables:
        print(f"- {table['name']}")
    print()

    # Show current cities
    print("=== Current Cities ===")
    cursor.execute("SELECT * FROM cities")
    cities = cursor.fetchall()
    for city in cities:
        print(f"ID: {city['id']}, RU: {city['name_ru']}, KK: {city['name_kk']}")

    # Show current districts
    print("\n=== Current Districts ===")
    cursor.execute("SELECT d.*, c.name_ru as city_name FROM districts d JOIN cities c ON d.city_id = c.id ORDER BY c.name_ru, d.name_ru")
    districts = cursor.fetchall()
    for district in districts:
        print(f"ID: {district['id']}, City: {district['city_name']}, RU: {district['name_ru']}, KK: {district['name_kk']}")

    print("\n=== Cleaning Database ===")

    # Keep only Almaty and Astana
    cities_to_keep = ['Алматы', 'Астана']

    # Get IDs of cities to keep
    city_ids_to_keep = []
    for city_name in cities_to_keep:
        cursor.execute("SELECT id FROM cities WHERE name_ru = ?", (city_name,))
        result = cursor.fetchone()
        if result:
            city_ids_to_keep.append(result['id'])

    print(f"Keeping cities with IDs: {city_ids_to_keep}")

    if city_ids_to_keep:
        # Delete cities not in the list
        placeholders = ','.join('?' * len(city_ids_to_keep))
        cursor.execute(f"DELETE FROM cities WHERE id NOT IN ({placeholders})", city_ids_to_keep)
        deleted_cities = cursor.rowcount
        print(f"Deleted {deleted_cities} cities")

        # Delete districts for deleted cities
        cursor.execute(f"DELETE FROM districts WHERE city_id NOT IN ({placeholders})", city_ids_to_keep)
        deleted_districts = cursor.rowcount
        print(f"Deleted {deleted_districts} districts from removed cities")

        # Remove duplicate districts (keep first occurrence)
        cursor.execute("""
            DELETE FROM districts
            WHERE id NOT IN (
                SELECT MIN(id)
                FROM districts
                GROUP BY city_id, name_ru, name_kk
            )
        """)
        deleted_duplicates = cursor.rowcount
        print(f"Deleted {deleted_duplicates} duplicate districts")

    conn.commit()

    # Show final state
    print("\n=== Final Cities ===")
    cursor.execute("SELECT * FROM cities")
    cities = cursor.fetchall()
    for city in cities:
        print(f"ID: {city['id']}, RU: {city['name_ru']}, KK: {city['name_kk']}")

    print("\n=== Final Districts ===")
    cursor.execute("SELECT d.*, c.name_ru as city_name FROM districts d JOIN cities c ON d.city_id = c.id ORDER BY c.name_ru, d.name_ru")
    districts = cursor.fetchall()
    for district in districts:
        print(f"ID: {district['id']}, City: {district['city_name']}, RU: {district['name_ru']}, KK: {district['name_kk']}")

    conn.close()
    print("\n✅ Database cleanup completed!")

if __name__ == "__main__":
    main()
