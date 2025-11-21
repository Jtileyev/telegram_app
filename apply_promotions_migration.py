#!/usr/bin/env python3
"""
Migration script to add promotions system to existing database
This script will:
1. Create promotions table
2. Create user_promotion_progress table
3. Add promotion_id field to apartments table (replacing old promotion text field)
4. Add promotion fields to bookings table
5. Create necessary indexes
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / 'database' / 'rental.db'

def apply_migration():
    """Apply promotions migration to database"""
    print("🔄 Starting promotions migration...")

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    try:
        # Check if promotions table already exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='promotions'")
        if cursor.fetchone():
            print("⚠️  Promotions table already exists. Skipping migration.")
            return

        # 1. Create promotions table
        print("📊 Creating promotions table...")
        cursor.execute("""
            CREATE TABLE promotions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                bookings_required INTEGER NOT NULL,
                free_days INTEGER NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 2. Create user_promotion_progress table
        print("📊 Creating user_promotion_progress table...")
        cursor.execute("""
            CREATE TABLE user_promotion_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                apartment_id INTEGER NOT NULL,
                promotion_id INTEGER NOT NULL,
                completed_bookings INTEGER DEFAULT 0,
                cycle_number INTEGER DEFAULT 1,
                last_booking_id INTEGER,
                bonus_applied_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (apartment_id) REFERENCES apartments(id) ON DELETE CASCADE,
                FOREIGN KEY (promotion_id) REFERENCES promotions(id) ON DELETE CASCADE,
                FOREIGN KEY (last_booking_id) REFERENCES bookings(id),
                UNIQUE(user_id, apartment_id, promotion_id)
            )
        """)

        # 3. Check if old promotion column exists in apartments
        cursor.execute("PRAGMA table_info(apartments)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'promotion' in columns and 'promotion_id' not in columns:
            print("🔄 Migrating apartments table...")
            # SQLite doesn't support DROP COLUMN, so we need to recreate the table
            # But for simplicity, we'll just add the new column
            cursor.execute("ALTER TABLE apartments ADD COLUMN promotion_id INTEGER REFERENCES promotions(id) ON DELETE SET NULL")
            print("✅ Added promotion_id column to apartments")
        elif 'promotion_id' not in columns:
            cursor.execute("ALTER TABLE apartments ADD COLUMN promotion_id INTEGER REFERENCES promotions(id) ON DELETE SET NULL")
            print("✅ Added promotion_id column to apartments")

        # 4. Add promotion fields to bookings table if they don't exist
        cursor.execute("PRAGMA table_info(bookings)")
        booking_columns = [col[1] for col in cursor.fetchall()]

        if 'promotion_id' not in booking_columns:
            print("🔄 Adding promotion fields to bookings table...")
            cursor.execute("ALTER TABLE bookings ADD COLUMN promotion_id INTEGER REFERENCES promotions(id)")
            cursor.execute("ALTER TABLE bookings ADD COLUMN promotion_discount_days INTEGER DEFAULT 0")
            cursor.execute("ALTER TABLE bookings ADD COLUMN original_price REAL")
            print("✅ Added promotion fields to bookings")

        # 5. Create indexes
        print("📇 Creating indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_promotions_active ON promotions(is_active)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_apartments_promotion ON apartments(promotion_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_bookings_promotion ON bookings(promotion_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_promotion_progress_user ON user_promotion_progress(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_promotion_progress_apartment ON user_promotion_progress(apartment_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_promotion_progress_user_apartment ON user_promotion_progress(user_id, apartment_id)")

        # 6. Insert example promotions
        print("📝 Creating example promotions...")
        cursor.execute("""
            INSERT INTO promotions (name, description, bookings_required, free_days, is_active)
            VALUES
                ('Акция "6+1"', 'Каждое 6-е заселение - 1 бесплатный день', 6, 1, 1),
                ('Акция "3+2"', 'Каждое 3-е заселение - 2 бесплатных дня', 3, 2, 0),
                ('Акция "10+3"', 'Каждое 10-е заселение - 3 бесплатных дня', 10, 3, 0)
        """)

        conn.commit()
        print("✅ Migration completed successfully!")
        print("\n📋 Created:")
        print("   - promotions table")
        print("   - user_promotion_progress table")
        print("   - promotion_id field in apartments")
        print("   - promotion fields in bookings")
        print("   - 3 example promotions")
        print("\n💡 Next steps:")
        print("   1. Go to admin panel → Акции")
        print("   2. Enable/edit promotions as needed")
        print("   3. Assign promotions to apartments")

    except sqlite3.Error as e:
        print(f"❌ Error during migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    if not DB_PATH.exists():
        print(f"❌ Database not found at {DB_PATH}")
        print("   Please run init_database.py first")
        exit(1)

    apply_migration()
