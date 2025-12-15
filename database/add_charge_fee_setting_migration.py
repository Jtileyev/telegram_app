#!/usr/bin/env python3
"""
Migration: Add charge_fee_for_admins setting
Date: 2025-12-15
Description: Adds setting to control whether platform fee is charged for admin landlords' apartments
"""

import sqlite3
import os

# Get database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'rental.db')

def migrate():
    """Add charge_fee_for_admins setting"""
    conn = sqlite3.connect(DB_PATH)
    
    try:
        # Check if setting already exists
        cursor = conn.execute("SELECT 1 FROM settings WHERE key = 'charge_fee_for_admins'")
        if cursor.fetchone():
            print("✓ Setting 'charge_fee_for_admins' already exists")
            return
        
        # Add new setting
        conn.execute("""
            INSERT INTO settings (key, value, description)
            VALUES ('charge_fee_for_admins', '0', 'Взимать комиссию с квартир администраторов')
        """)
        conn.commit()
        print("✓ Added setting 'charge_fee_for_admins' with value '0' (disabled)")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("Running migration: add_charge_fee_for_admins_setting")
    migrate()
    print("Migration complete!")
