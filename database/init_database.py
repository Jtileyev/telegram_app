#!/usr/bin/env python3
"""
Initialize database with default admin and test data
Creates cities, districts, and sample apartments
"""

import sqlite3
import json
import secrets
import string
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_PATH = Path(__file__).parent / 'rental.db'

def generate_password(length=12):
    """Generate a random password"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(alphabet) for i in range(length))
    return password

def hash_password_bcrypt(password):
    """Hash password using bcrypt (PHP compatible)"""
    try:
        import bcrypt
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        return hashed.decode()
    except ImportError:
        print("⚠️  bcrypt not available, installing...")
        import subprocess
        import sys
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "bcrypt"])
            import bcrypt
            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            return hashed.decode()
        except:
            print("⚠️  Could not install bcrypt. Using compatible password.")
            # Use a simple known password for initial setup
            # Admin can change it later through the admin panel
            return '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi'  # "admin"

def main():
    if not DB_PATH.exists():
        print(f"Error: Database not found at {DB_PATH}")
        print("Please run schema migration first")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("="*60)
    print("DATABASE INITIALIZATION")
    print("="*60)

    # Get admin credentials from environment or use defaults
    admin_email = os.getenv('ADMIN_EMAIL', 'atks0513@gmail.com')
    admin_password_env = os.getenv('ADMIN_PASSWORD')

    # Use password from environment if set, otherwise generate random
    if admin_password_env:
        admin_password = admin_password_env
        print(f"\n📧 Admin Email: {admin_email}")
        print(f"🔑 Password: (from .env file)")
        print("\n✓ Using password from environment variables")
    else:
        # Try to use bcrypt, fall back to simple password if not available
        try:
            import bcrypt
            admin_password = generate_password()
            print(f"\n📧 Admin Email: {admin_email}")
            print(f"🔑 Generated Password: {admin_password}")
            print("\n⚠️  SAVE THIS PASSWORD!")
            print("💡 Tip: You can set ADMIN_PASSWORD in .env file to use a custom password")
        except ImportError:
            admin_password = "admin"
            print(f"\n📧 Admin Email: {admin_email}")
            print(f"🔑 Default Password: {admin_password}")
            print("\n⚠️  Using default password. Please change it after first login!")
            print("💡 Tip: Install bcrypt for secure password generation: pip install bcrypt")

    # 1. Create/Update default admin
    print("\n1. Setting up admin user...")
    cursor.execute("SELECT * FROM users WHERE email = ?", (admin_email,))
    existing_admin = cursor.fetchone()

    if existing_admin:
        # Update existing admin
        cursor.execute("""
            UPDATE users
            SET password = ?,
                roles = ?,
                full_name = 'Администратор',
                is_active = 1,
                updated_at = CURRENT_TIMESTAMP
            WHERE email = ?
        """, (hash_password_bcrypt(admin_password), json.dumps(['admin', 'landlord']), admin_email))
        admin_id = existing_admin['id']
        print(f"   ✓ Updated existing admin (ID: {admin_id})")
    else:
        # Create new admin
        cursor.execute("""
            INSERT INTO users (email, password, full_name, phone, roles, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, 1, CURRENT_TIMESTAMP)
        """, (
            admin_email,
            hash_password_bcrypt(admin_password),
            'Администратор',
            '+7 777 123 45 67',
            json.dumps(['admin', 'landlord'])
        ))
        admin_id = cursor.lastrowid
        print(f"   ✓ Created new admin (ID: {admin_id})")

    # 2. Clear existing cities and districts
    print("\n2. Clearing old location data...")
    cursor.execute("DELETE FROM apartments")
    cursor.execute("DELETE FROM districts")
    cursor.execute("DELETE FROM cities")
    print("   ✓ Cleared all cities, districts, and apartments")

    # 3. Create cities
    print("\n3. Creating cities...")
    cities_data = [
        ('Алматы', 'Алматы'),
        ('Астана', 'Астана')
    ]

    city_ids = {}
    for name_ru, name_kk in cities_data:
        cursor.execute("""
            INSERT INTO cities (name_ru, name_kk, created_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (name_ru, name_kk))
        city_id = cursor.lastrowid
        city_ids[name_ru] = city_id
        print(f"   ✓ Created city: {name_ru} (ID: {city_id})")

    # 4. Create districts
    print("\n4. Creating districts...")
    districts_data = {
        'Алматы': [
            ('Алмалинский район', 'Алмалы ауданы'),
            ('Бостандыкский район', 'Бостандық ауданы'),
            ('Медеуский район', 'Медеу ауданы'),
            ('Ауэзовский район', 'Әуезов ауданы'),
            ('Жетысуский район', 'Жетісу ауданы'),
            ('Наурызбайский район', 'Наурызбай ауданы'),
            ('Турксибский район', 'Түрксіб ауданы'),
            ('Алатауский район', 'Алатау ауданы')
        ],
        'Астана': [
            ('Есильский район', 'Есіл ауданы'),
            ('Алматинский район', 'Алматы ауданы'),
            ('Сарыаркинский район', 'Сарыарқа ауданы'),
            ('Байконурский район', 'Байқоңыр ауданы')
        ]
    }

    district_ids = {}
    for city_name, districts in districts_data.items():
        city_id = city_ids[city_name]
        district_ids[city_name] = []

        for name_ru, name_kk in districts:
            cursor.execute("""
                INSERT INTO districts (city_id, name_ru, name_kk, created_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (city_id, name_ru, name_kk))
            district_id = cursor.lastrowid
            district_ids[city_name].append(district_id)
            print(f"   ✓ Created district: {name_ru} in {city_name}")

    # 5. Create test apartments
    print("\n5. Creating test apartments...")

    test_apartments = [
        {
            'city': 'Алматы',
            'district_index': 0,  # Алмалинский район
            'title_ru': 'Современная 2-комнатная квартира в центре',
            'title_kk': 'Орталықтағы қазіргі заманғы 2 бөлмелі пәтер',
            'description_ru': 'Уютная квартира с евроремонтом в самом центре города. Вся необходимая мебель и техника. Рядом метро, магазины, рестораны.',
            'description_kk': 'Қаланың орталығында еуроремонты бар жайлы пәтер. Барлық қажетті жиһаз бен техника. Жанында метро, дүкендер, мейрамханалар.',
            'address': 'ул. Абая, 150',
            'price_per_day': 15000,
            'price_per_month': 350000,
            'gis_link': 'https://2gis.kz/almaty',
            'amenities': ['Wi-Fi', 'Кондиционер', 'Телевизор', 'Холодильник', 'Стиральная машина', 'Кухня', 'Ванная', '2 комнаты', '65 м²', '5 этаж']
        },
        {
            'city': 'Алматы',
            'district_index': 1,  # Бостандыкский район
            'title_ru': 'Студия рядом с метро',
            'title_kk': 'Метроның жанындағы студия',
            'description_ru': 'Компактная студия для одного или двух человек. 5 минут пешком до метро. Отличный вариант для командировок.',
            'description_kk': 'Бір немесе екі адамға арналған ықшам студия. Метроға 5 минут жаяу. Іссапарларға тамаша нұсқа.',
            'address': 'ул. Толе би, 45',
            'price_per_day': 10000,
            'price_per_month': 250000,
            'amenities': ['Wi-Fi', 'Телевизор', 'Холодильник', 'Микроволновка', 'Студия', '30 м²', '3 этаж']
        },
        {
            'city': 'Алматы',
            'district_index': 2,  # Медеуский район
            'title_ru': '3-комнатная квартира с видом на горы',
            'title_kk': 'Таулардың көрінісі бар 3 бөлмелі пәтер',
            'description_ru': 'Просторная квартира с панорамным видом на горы. Идеально для семейного отдыха. Три спальни, большая кухня-гостиная.',
            'description_kk': 'Таулардың панорамалық көрінісі бар кең пәтер. Отбасылық демалыс үшін өте жақсы. Үш жатын бөлме, үлкен асхана-қонақ бөлме.',
            'address': 'пр. Аль-Фараби, 77',
            'price_per_day': 25000,
            'price_per_month': 600000,
            'gis_link': 'https://2gis.kz/almaty',
            'amenities': ['Wi-Fi', 'Кондиционер', 'Телевизор', 'Холодильник', 'Стиральная машина', 'Посудомоечная машина', '3 комнаты', '95 м²', '12 этаж', 'Балкон', 'Парковка']
        },
        {
            'city': 'Астана',
            'district_index': 0,  # Есильский район
            'title_ru': 'Современная квартира в бизнес-центре',
            'title_kk': 'Іскер орталықтағы қазіргі заманғы пәтер',
            'description_ru': 'Новая квартира в престижном районе Астаны. Отличная планировка, дизайнерский ремонт.',
            'description_kk': 'Астананың беделді ауданындағы жаңа пәтер. Тамаша жоспарлау, дизайнерлік жөндеу.',
            'address': 'пр. Кабанбай батыра, 42',
            'price_per_day': 18000,
            'price_per_month': 450000,
            'amenities': ['Wi-Fi', 'Кондиционер', 'Телевизор', 'Холодильник', 'Стиральная машина', '2 комнаты', '70 м²', '8 этаж', 'Охрана']
        },
        {
            'city': 'Астана',
            'district_index': 2,  # Сарыаркинский район
            'title_ru': 'Уютная квартира в спальном районе',
            'title_kk': 'Ұйқы ауданындағы жайлы пәтер',
            'description_ru': 'Тихая квартира в спальном районе. Рядом школы, детские сады, магазины. Отличное место для семьи.',
            'description_kk': 'Ұйқы ауданындағы тыныш пәтер. Жанында мектептер, балабақшалар, дүкендер. Отбасыға тамаша орын.',
            'address': 'ул. Сыганак, 18',
            'price_per_day': 12000,
            'price_per_month': 300000,
            'amenities': ['Wi-Fi', 'Телевизор', 'Холодильник', 'Стиральная машина', '2 комнаты', '55 м²', '4 этаж']
        }
    ]

    created_count = 0
    for apt in test_apartments:
        city_id = city_ids[apt['city']]
        district_id = district_ids[apt['city']][apt['district_index']]

        cursor.execute("""
            INSERT INTO apartments (
                landlord_id, city_id, district_id,
                title_ru, title_kk, description_ru, description_kk,
                address, price_per_day, price_per_month, gis_link,
                amenities, is_active, rating, reviews_count,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 0.0, 0, CURRENT_TIMESTAMP)
        """, (
            admin_id, city_id, district_id,
            apt['title_ru'], apt['title_kk'],
            apt['description_ru'], apt['description_kk'],
            apt['address'], apt['price_per_day'], apt.get('price_per_month'),
            apt.get('gis_link'),
            json.dumps(apt['amenities'], ensure_ascii=False)
        ))
        created_count += 1
        print(f"   ✓ Created: {apt['title_ru']} in {apt['city']}")

    # Commit all changes
    conn.commit()
    conn.close()

    # Apply migrations
    print("\n6. Applying database migrations...")
    try:
        from migrate import apply_migrations
        apply_migrations()
    except Exception as e:
        print(f"   ⚠️  Migration warning: {e}")

    print("\n" + "="*60)
    print("✅ Database initialized successfully!")
    print("="*60)
    print("\n📋 Summary:")
    print(f"  • Cities created: {len(cities_data)}")
    print(f"  • Districts created: {sum(len(d) for d in districts_data.values())}")
    print(f"  • Test apartments created: {created_count}")
    print("\n🔐 Admin credentials:")
    print(f"  Email: {admin_email}")
    print(f"  Password: {admin_password}")
    print("\n⚠️  IMPORTANT: Save the password above!")
    print("\nYou can now:")
    print("  1. Login to admin panel with these credentials")
    print("  2. Start the Telegram bot")
    print("  3. Test apartment listings")

if __name__ == "__main__":
    main()
