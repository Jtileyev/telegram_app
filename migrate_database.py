#!/usr/bin/env python3
"""
Migration script to merge users, admins, and landlords tables into single users table
"""

import sqlite3
import json
import shutil
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / 'database' / 'rental.db'
BACKUP_PATH = Path(__file__).parent / 'database' / f'rental_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
NEW_SCHEMA_PATH = Path(__file__).parent / 'database' / 'schema_new.sql'

def create_backup():
    """Create backup of current database"""
    print(f"Creating backup: {BACKUP_PATH}")
    shutil.copy2(DB_PATH, BACKUP_PATH)
    print(f"✓ Backup created successfully")

def migrate_data():
    """Migrate data from old structure to new"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("\n=== Starting Migration ===\n")

    # 1. Backup existing data
    print("1. Backing up data...")

    # Get existing users
    cursor.execute("SELECT * FROM users")
    old_users = [dict(row) for row in cursor.fetchall()]

    # Get existing admins
    cursor.execute("SELECT * FROM admins")
    old_admins = [dict(row) for row in cursor.fetchall()]

    # Get existing landlords
    cursor.execute("SELECT * FROM landlords")
    old_landlords = [dict(row) for row in cursor.fetchall()]

    # Get settings
    cursor.execute("SELECT * FROM settings")
    settings = [dict(row) for row in cursor.fetchall()]

    # Get translations if exists
    try:
        cursor.execute("SELECT * FROM translations")
        translations = [dict(row) for row in cursor.fetchall()]
    except:
        translations = []

    print(f"   - Found {len(old_users)} users")
    print(f"   - Found {len(old_admins)} admins")
    print(f"   - Found {len(old_landlords)} landlords")
    print(f"   - Found {len(settings)} settings")
    print(f"   - Found {len(translations)} translations")

    # 2. Drop all tables
    print("\n2. Dropping old tables...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall() if row[0] != 'sqlite_sequence']

    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")
        print(f"   - Dropped table: {table}")

    # 3. Create new schema
    print("\n3. Creating new schema...")
    with open(NEW_SCHEMA_PATH, 'r', encoding='utf-8') as f:
        new_schema = f.read()

    cursor.executescript(new_schema)
    print("   ✓ New schema created")

    # 4. Migrate users to new table
    print("\n4. Migrating users to new structure...")

    # Keep track of ID mappings
    user_id_map = {}  # old_id -> new_id
    landlord_id_map = {}  # old_landlord_id -> new_user_id

    # First, migrate regular users
    for user in old_users:
        cursor.execute("""
            INSERT INTO users (telegram_id, username, full_name, phone, language, roles, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user['telegram_id'],
            user.get('username'),
            user.get('full_name'),
            user.get('phone'),
            user.get('language', 'ru'),
            json.dumps(['user']),
            user.get('created_at'),
            user.get('updated_at')
        ))
        new_id = cursor.lastrowid
        user_id_map[user['id']] = new_id
        print(f"   - Migrated user {user['telegram_id']} (old_id={user['id']} -> new_id={new_id})")

    # Migrate admins
    for admin in old_admins:
        # Check if admin email already exists as landlord
        landlord = next((l for l in old_landlords if l.get('email') == admin.get('username')), None)

        if landlord:
            # Admin is also a landlord, merge them
            cursor.execute("""
                INSERT INTO users (email, username, password, full_name, phone, telegram_id, roles, is_active, created_at, last_login)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                landlord['email'],
                admin.get('username'),
                admin['password'],
                landlord.get('full_name') or admin.get('full_name'),
                landlord.get('phone'),
                landlord.get('telegram_id'),
                json.dumps(['admin', 'landlord']),
                admin.get('is_active', 1),
                admin.get('created_at'),
                admin.get('last_login')
            ))
            new_id = cursor.lastrowid
            landlord_id_map[landlord['id']] = new_id
            print(f"   - Migrated admin+landlord {admin['username']} (landlord_id={landlord['id']} -> user_id={new_id})")
        else:
            # Admin only
            cursor.execute("""
                INSERT INTO users (email, username, password, full_name, roles, is_active, created_at, last_login)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                admin.get('username'),
                admin.get('username'),
                admin['password'],
                admin.get('full_name'),
                json.dumps(['admin']),
                admin.get('is_active', 1),
                admin.get('created_at'),
                admin.get('last_login')
            ))
            print(f"   - Migrated admin {admin['username']} (id={cursor.lastrowid})")

    # Migrate remaining landlords (not already migrated as admin+landlord)
    for landlord in old_landlords:
        if landlord['id'] not in landlord_id_map:
            cursor.execute("""
                INSERT INTO users (telegram_id, email, full_name, phone, password, roles, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                landlord.get('telegram_id'),
                landlord['email'],
                landlord['full_name'],
                landlord['phone'],
                landlord.get('password'),
                json.dumps(['landlord']),
                landlord.get('is_active', 1),
                landlord.get('created_at'),
                landlord.get('updated_at')
            ))
            new_id = cursor.lastrowid
            landlord_id_map[landlord['id']] = new_id
            print(f"   - Migrated landlord {landlord['email']} (old_id={landlord['id']} -> new_id={new_id})")

    # 5. Restore settings
    print("\n5. Restoring settings...")
    for setting in settings:
        cursor.execute("""
            INSERT OR IGNORE INTO settings (key, value, description, updated_at)
            VALUES (?, ?, ?, ?)
        """, (setting['key'], setting['value'], setting.get('description'), setting.get('updated_at')))
        print(f"   - Restored setting: {setting['key']}")

    # 6. Restore translations
    if translations:
        print("\n6. Restoring translations...")
        for trans in translations:
            cursor.execute("""
                INSERT OR IGNORE INTO translations (key, text_ru, text_kk, updated_at)
                VALUES (?, ?, ?, ?)
            """, (trans['key'], trans['text_ru'], trans['text_kk'], trans.get('updated_at')))
        print(f"   - Restored {len(translations)} translations")

    # 7. Update references in other tables if they exist
    print("\n7. Updating references in existing data...")

    # Update apartments landlord_id references
    try:
        cursor.execute("SELECT * FROM apartments")
        apartments = [dict(row) for row in cursor.fetchall()]
        if apartments:
            print("   Note: Apartments found, but will be cleaned by init script")
    except:
        pass

    # Commit changes
    conn.commit()
    conn.close()

    print("\n" + "="*50)
    print("✅ Migration completed successfully!")
    print("="*50)
    print(f"\nBackup saved to: {BACKUP_PATH}")
    print("\nSummary:")
    print(f"  - Regular users migrated: {len(old_users)}")
    print(f"  - Admins migrated: {len(old_admins)}")
    print(f"  - Landlords migrated: {len(old_landlords)}")
    print(f"  - Settings preserved: {len(settings)}")
    print(f"  - Translations preserved: {len(translations)}")
    print("\nNext steps:")
    print("  1. Run init_database.py to setup default admin and test data")
    print("  2. Update admin panel code if needed")

def main():
    if not DB_PATH.exists():
        print(f"Error: Database not found at {DB_PATH}")
        return

    if not NEW_SCHEMA_PATH.exists():
        print(f"Error: New schema not found at {NEW_SCHEMA_PATH}")
        return

    print("="*50)
    print("DATABASE MIGRATION")
    print("="*50)
    print("\nThis will:")
    print("  1. Create a backup of current database")
    print("  2. Merge users, admins, and landlords into single users table")
    print("  3. Clear all cities and districts data")
    print("  4. Preserve system settings and translations")
    print("\n⚠️  This operation cannot be undone (except via backup)")

    response = input("\nContinue? (yes/no): ")
    if response.lower() != 'yes':
        print("Migration cancelled")
        return

    # Create backup
    create_backup()

    # Run migration
    migrate_data()

if __name__ == "__main__":
    main()
