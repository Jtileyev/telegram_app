#!/usr/bin/env python3
"""Setup admin user and create test data"""

import sqlite3
import hashlib
from pathlib import Path

DB_PATH = Path(__file__).parent / 'database' / 'rental.db'

def hash_password(password):
    """Hash password using MD5 (matches PHP password_hash alternative)"""
    return hashlib.md5(password.encode()).hexdigest()

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("=== Setting up admin and test data ===\n")

    # 1. Run migrations
    print("1. Running migrations...")

    # Translations table
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS translations (
            key TEXT PRIMARY KEY,
            text_ru TEXT NOT NULL,
            text_kk TEXT NOT NULL,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_translations_key ON translations(key);
    """)
    print("   ✓ Translations table created")

    # 2. Update admin username
    print("\n2. Updating admin username...")
    cursor.execute("SELECT * FROM admins WHERE username = 'admin'")
    old_admin = cursor.fetchone()

    if old_admin:
        # Update existing admin to new username
        cursor.execute("""
            UPDATE admins
            SET username = 'atks0513@gmail.com'
            WHERE username = 'admin'
        """)
        print(f"   ✓ Admin username updated from 'admin' to 'atks0513@gmail.com'")
        print(f"   Password remains: admin")
        admin_id = old_admin['id']
    else:
        # Check if new admin already exists
        cursor.execute("SELECT * FROM admins WHERE username = 'atks0513@gmail.com'")
        existing = cursor.fetchone()
        if not existing:
            # Create new admin
            cursor.execute("""
                INSERT INTO admins (username, password, full_name, created_at)
                VALUES ('atks0513@gmail.com', ?, 'Administrator', CURRENT_TIMESTAMP)
            """, (hash_password('admin'),))
            admin_id = cursor.lastrowid
            print(f"   ✓ Admin created: atks0513@gmail.com / admin")
        else:
            admin_id = existing['id']
            print(f"   ✓ Admin atks0513@gmail.com already exists")

    # 3. Create landlord from admin
    print("\n3. Creating landlord profile for admin...")

    cursor.execute("SELECT id FROM landlords WHERE email = 'atks0513@gmail.com'")
    landlord = cursor.fetchone()

    if not landlord:
        cursor.execute("""
            INSERT INTO landlords (full_name, phone, email, telegram_id, is_active, created_at)
            VALUES ('Администратор', '+7 777 123 45 67', 'atks0513@gmail.com', NULL, 1, CURRENT_TIMESTAMP)
        """)
        landlord_id = cursor.lastrowid
        print(f"   ✓ Landlord created with ID: {landlord_id}")
    else:
        landlord_id = landlord['id']
        print(f"   ✓ Landlord already exists with ID: {landlord_id}")

    # 4. Get cities and districts
    print("\n4. Getting cities and districts...")
    cursor.execute("SELECT * FROM cities WHERE name_ru IN ('Алматы', 'Астана')")
    cities = {row['name_ru']: row['id'] for row in cursor.fetchall()}

    if not cities:
        print("   ✗ No cities found! Run cleanup_db.py first")
        conn.close()
        return

    almaty_id = cities.get('Алматы')
    astana_id = cities.get('Астана')

    print(f"   Алматы ID: {almaty_id}")
    print(f"   Астана ID: {astana_id}")

    # Get districts
    districts = {}
    if almaty_id:
        cursor.execute("SELECT * FROM districts WHERE city_id = ?", (almaty_id,))
        districts['Алматы'] = [row for row in cursor.fetchall()]
    if astana_id:
        cursor.execute("SELECT * FROM districts WHERE city_id = ?", (astana_id,))
        districts['Астана'] = [row for row in cursor.fetchall()]

    # 5. Create test apartments
    print("\n5. Creating test apartments...")

    test_apartments = [
        {
            'title_ru': 'Современная 2-комнатная квартира в центре',
            'title_kk': 'Орталықтағы қазіргі заманғы 2 бөлмелі пәтер',
            'description_ru': 'Уютная квартира с евроремонтом в самом центре города. Все необходимое для комфортного проживания.',
            'description_kk': 'Қаланың орталығында еуроремонты бар жайлы пәтер. Жайлы өмір сүру үшін қажет барлығы.',
            'city': 'Алматы',
            'address': 'ул. Абая, 150',
            'price_per_day': 15000,
            'amenities': '["Wi-Fi", "Кондиционер", "Телевизор", "Холодильник", "Стиральная машина", "2 комнаты", "65 м²", "5 этаж"]'
        },
        {
            'title_ru': 'Студия рядом с метро Алмалы',
            'title_kk': 'Алмалы метросының жанындағы студия',
            'description_ru': 'Отличная студия для одного или двух человек. 5 минут до метро Алмалы.',
            'description_kk': 'Бір немесе екі адамға арналған тамаша студия. Алмалы метросына 5 минут.',
            'city': 'Алматы',
            'address': 'ул. Толе би, 45',
            'price_per_day': 10000,
            'amenities': '["Wi-Fi", "Телевизор", "Холодильник", "Студия", "30 м²", "3 этаж"]'
        },
        {
            'title_ru': '3-комнатная квартира с видом на горы',
            'title_kk': 'Таулардың көрінісі бар 3 бөлмелі пәтер',
            'description_ru': 'Просторная квартира с панорамным видом на горы. Идеально для семейного отдыха.',
            'description_kk': 'Таулардың панорамалық көрінісі бар кең пәтер. Отбасылық демалыс үшін өте жақсы.',
            'city': 'Алматы',
            'address': 'пр. Аль-Фараби, 77',
            'price_per_day': 25000,
            'amenities': '["Wi-Fi", "Кондиционер", "Телевизор", "Холодильник", "Стиральная машина", "Посудомоечная машина", "3 комнаты", "95 м²", "12 этаж"]'
        },
        {
            'title_ru': 'Современная квартира в Астане',
            'title_kk': 'Астанадағы қазіргі заманғы пәтер',
            'description_ru': 'Новая квартира в престижном районе Астаны. Отличная планировка.',
            'description_kk': 'Астананың беделді ауданындағы жаңа пәтер. Тамаша жоспарлау.',
            'city': 'Астана',
            'address': 'пр. Кабанбай батыра, 42',
            'price_per_day': 18000,
            'amenities': '["Wi-Fi", "Кондиционер", "Телевизор", "Холодильник", "Стиральная машина", "2 комнаты", "70 м²", "8 этаж"]'
        },
        {
            'title_ru': 'Уютная квартира в Есильском районе',
            'title_kk': 'Есіл ауданындағы жайлы пәтер',
            'description_ru': 'Тихая квартира в спальном районе. Рядом все необходимое.',
            'description_kk': 'Ұйқы ауданындағы тыныш пәтер. Жанында қажеттінің бәрі.',
            'city': 'Астана',
            'address': 'ул. Сыганак, 18',
            'price_per_day': 12000,
            'amenities': '["Wi-Fi", "Телевизор", "Холодильник", "1 комната", "45 м²", "4 этаж"]'
        }
    ]

    created_count = 0
    for apt in test_apartments:
        city_id = cities.get(apt['city'])
        if not city_id:
            print(f"   ✗ Skipping apartment in {apt['city']}: city not found")
            continue

        # Get first district for this city
        city_districts = districts.get(apt['city'], [])
        if not city_districts:
            print(f"   ✗ Skipping apartment in {apt['city']}: no districts found")
            continue

        district_id = city_districts[0]['id']

        # Check if apartment already exists
        cursor.execute("""
            SELECT id FROM apartments
            WHERE address = ? AND city_id = ?
        """, (apt['address'], city_id))

        if cursor.fetchone():
            print(f"   - Apartment at {apt['address']} already exists")
            continue

        # Insert apartment
        cursor.execute("""
            INSERT INTO apartments (
                landlord_id, city_id, district_id,
                title_ru, title_kk, description_ru, description_kk,
                address, price_per_day,
                amenities, is_active, rating, reviews_count,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 0.0, 0, CURRENT_TIMESTAMP)
        """, (
            landlord_id, city_id, district_id,
            apt['title_ru'], apt['title_kk'],
            apt['description_ru'], apt['description_kk'],
            apt['address'], apt['price_per_day'],
            apt['amenities']
        ))
        created_count += 1
        print(f"   ✓ Created: {apt['title_ru']}")

    print(f"\n   Total apartments created: {created_count}")

    # Commit all changes
    conn.commit()
    conn.close()

    print("\n" + "="*50)
    print("✅ Setup completed successfully!")
    print("="*50)
    print("\nAdmin credentials:")
    print("  Email: atks0513@gmail.com")
    print("  Password: admin")
    print("\nAdmin is also a landlord and can manage apartments!")

if __name__ == "__main__":
    main()
