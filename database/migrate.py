#!/usr/bin/env python3
"""
Database migration system for Astavaisya
"""
import sqlite3
from pathlib import Path

MIGRATIONS_DIR = Path(__file__).parent / 'migrations'
DB_PATH = Path(__file__).parent / 'rental.db'


def get_connection():
    """Get database connection"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def get_applied_migrations(conn) -> set:
    """Get set of applied migration names"""
    # Create migrations table if not exists
    conn.execute('''
        CREATE TABLE IF NOT EXISTS migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()

    cursor = conn.execute('SELECT name FROM migrations ORDER BY id')
    return {row['name'] for row in cursor.fetchall()}


def apply_migrations():
    """Apply all pending migrations"""
    if not DB_PATH.exists():
        print(f"Database not found: {DB_PATH}")
        print("Run init_database.py first")
        return False

    if not MIGRATIONS_DIR.exists():
        print(f"Migrations directory not found: {MIGRATIONS_DIR}")
        return False

    conn = get_connection()
    applied = get_applied_migrations(conn)

    # Get all migration files sorted by name
    migration_files = sorted(MIGRATIONS_DIR.glob('*.sql'))

    if not migration_files:
        print("No migration files found")
        conn.close()
        return True

    pending_count = 0
    for migration_file in migration_files:
        name = migration_file.name

        if name in applied:
            continue

        print(f"Applying migration: {name}")
        try:
            with open(migration_file, 'r', encoding='utf-8') as f:
                sql = f.read()

            conn.executescript(sql)
            conn.execute(
                'INSERT INTO migrations (name) VALUES (?)',
                (name,)
            )
            conn.commit()
            print(f"  ✓ Applied: {name}")
            pending_count += 1

        except Exception as e:
            print(f"  ✗ Failed: {name}")
            print(f"    Error: {e}")
            conn.rollback()
            conn.close()
            return False

    conn.close()

    if pending_count == 0:
        print("All migrations already applied")
    else:
        print(f"\n✓ Applied {pending_count} migration(s)")

    return True


def rollback_migration(name: str = None):
    """Rollback last migration or specific migration by name"""
    conn = get_connection()
    applied = get_applied_migrations(conn)

    if not applied:
        print("No migrations to rollback")
        conn.close()
        return True

    if name:
        if name not in applied:
            print(f"Migration not found: {name}")
            conn.close()
            return False
        target = name
    else:
        # Get last applied migration
        cursor = conn.execute(
            'SELECT name FROM migrations ORDER BY id DESC LIMIT 1'
        )
        row = cursor.fetchone()
        target = row['name'] if row else None

    if not target:
        print("No migration to rollback")
        conn.close()
        return True

    print(f"Rolling back: {target}")
    conn.execute('DELETE FROM migrations WHERE name = ?', (target,))
    conn.commit()
    conn.close()

    print(f"  ✓ Removed migration record: {target}")
    print("  Note: Database changes are NOT automatically reverted")
    return True


def list_migrations():
    """List all migrations and their status"""
    conn = get_connection()
    applied = get_applied_migrations(conn)
    conn.close()

    migration_files = sorted(MIGRATIONS_DIR.glob('*.sql'))

    print("\nMigrations:")
    print("-" * 50)

    for migration_file in migration_files:
        name = migration_file.name
        status = "✓ Applied" if name in applied else "○ Pending"
        print(f"  {status}: {name}")

    if not migration_files:
        print("  No migration files found")

    print("-" * 50)


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == 'list':
            list_migrations()
        elif command == 'rollback':
            name = sys.argv[2] if len(sys.argv) > 2 else None
            rollback_migration(name)
        elif command == 'apply':
            apply_migrations()
        else:
            print(f"Unknown command: {command}")
            print("Usage: python migrate.py [apply|list|rollback [name]]")
    else:
        apply_migrations()
