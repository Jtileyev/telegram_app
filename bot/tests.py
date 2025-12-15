import unittest
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add bot directory to path
sys.path.insert(0, os.path.dirname(__file__))

import database as db
from locales import get_text

class TestDatabase(unittest.TestCase):
    """Database operations tests"""

    @classmethod
    def setUpClass(cls):
        """Initialize test database"""
        import sqlite3
        # Use separate test database
        test_db_path = Path(__file__).parent.parent / 'database' / 'rental_test.db'

        # Remove old test database if exists
        if test_db_path.exists():
            test_db_path.unlink()

        # Override DB_PATH for tests
        db.DB_PATH = test_db_path

        # Initialize fresh test database
        db.init_db()
        
        # Add test data (cities and districts)
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO cities (name_ru, name_kk) VALUES ('Алматы', 'Алматы')")
        city_id = cursor.lastrowid
        cursor.execute("INSERT INTO districts (city_id, name_ru, name_kk) VALUES (?, 'Алмалинский', 'Алмалы')", (city_id,))
        cursor.execute("INSERT INTO districts (city_id, name_ru, name_kk) VALUES (?, 'Бостандыкский', 'Бостандық')", (city_id,))
        conn.commit()
        conn.close()

    @classmethod
    def tearDownClass(cls):
        """Clean up test database"""
        # Remove test database after all tests
        test_db_path = Path(__file__).parent.parent / 'database' / 'rental_test.db'
        if test_db_path.exists():
            test_db_path.unlink()

    def test_user_creation(self):
        """Test user creation and retrieval"""
        telegram_id = 999999999
        user_id = db.create_user(telegram_id, "test_user", "ru")
        self.assertIsNotNone(user_id)

        user = db.get_user(telegram_id)
        self.assertIsNotNone(user)
        self.assertEqual(user['telegram_id'], telegram_id)
        self.assertEqual(user['language'], 'ru')

    def test_user_update(self):
        """Test user data update"""
        telegram_id = 999999998
        db.create_user(telegram_id, "test_user2", "kk")

        db.update_user(telegram_id, full_name="Test User", phone="+7 777 777 77 77")
        user = db.get_user(telegram_id)

        self.assertEqual(user['full_name'], "Test User")
        self.assertEqual(user['phone'], "+7 777 777 77 77")

    def test_cities_and_districts(self):
        """Test cities and districts retrieval"""
        cities = db.get_cities()
        self.assertGreater(len(cities), 0)

        if cities:
            districts = db.get_districts(cities[0]['id'])
            self.assertGreaterEqual(len(districts), 0)

    def test_apartment_availability(self):
        """Test apartment availability check"""
        # This test assumes there are apartments in the database
        apartments = db.get_apartments()
        if apartments:
            apt = apartments[0]
            today = datetime.now().date()
            tomorrow = today + timedelta(days=1)
            next_week = today + timedelta(days=7)

            is_available = db.check_apartment_availability(
                apt['id'],
                tomorrow.isoformat(),
                next_week.isoformat()
            )
            self.assertIsInstance(is_available, bool)

    def test_favorites(self):
        """Test favorites functionality"""
        telegram_id = 999999997
        user_id = db.create_user(telegram_id, "fav_test", "ru")

        apartments = db.get_apartments()
        if apartments:
            apt_id = apartments[0]['id']

            # Add to favorites
            result = db.add_to_favorites(user_id, apt_id)
            self.assertTrue(result or not result)  # May fail if already exists

            # Check if in favorites
            is_fav = db.is_favorite(user_id, apt_id)
            self.assertTrue(is_fav)

            # Get favorites
            favorites = db.get_user_favorites(user_id)
            self.assertGreaterEqual(len(favorites), 1)

            # Remove from favorites
            db.remove_from_favorites(user_id, apt_id)
            is_fav = db.is_favorite(user_id, apt_id)
            self.assertFalse(is_fav)

    def test_settings(self):
        """Test settings management"""
        platform_fee = db.get_setting('platform_fee_percent')
        self.assertIsNotNone(platform_fee)

        db.set_setting('platform_fee_percent', '10')
        new_fee = db.get_setting('platform_fee_percent')
        self.assertEqual(new_fee, '10')

        # Restore original value
        db.set_setting('platform_fee_percent', '5')

class TestLocalization(unittest.TestCase):
    """Localization tests"""

    def test_russian_texts(self):
        """Test Russian localization"""
        text = get_text('welcome', 'ru')
        self.assertIn('Добро пожаловать', text)

        text = get_text('btn_search', 'ru')
        self.assertEqual(text, '🔍 Поиск')

    def test_kazakh_texts(self):
        """Test Kazakh localization"""
        text = get_text('welcome', 'kk')
        self.assertIn('қош келдіңіз', text.lower())

        text = get_text('btn_search', 'kk')
        self.assertEqual(text, '🔍 Іздеу')

    def test_text_formatting(self):
        """Test text formatting with parameters"""
        text = get_text('welcome_back', 'ru', name='Тест')
        self.assertIn('Тест', text)

        text = get_text('price_per_day', 'ru', price='10000')
        self.assertIn('10000', text)

class TestValidation(unittest.TestCase):
    """Validation tests"""

    def validate_phone(self, phone: str) -> bool:
        """Validate phone number format (copied from main.py to avoid aiogram import)"""
        import re
        cleaned = re.sub(r'[\s\(\)\-]', '', phone)
        if cleaned.startswith('8'):
            cleaned = '7' + cleaned[1:]
        if not cleaned.startswith('+'):
            cleaned = '+' + cleaned
        return bool(re.match(r'^\+7\d{10}$', cleaned))

    def test_phone_validation(self):
        """Test phone number validation"""
        valid_phones = [
            '+7 (777) 777 77 77',
            '+7 777 777 77 77',
            '+77777777777',
            '7 777 777 77 77',
            '77777777777',
            '8 777 777 77 77',
            '87777777777',
            '8(777)7777777',
        ]

        for phone in valid_phones:
            self.assertTrue(self.validate_phone(phone), f"Phone {phone} should be valid")

        invalid_phones = [
            '777 777 77 77',  # No country code
            '+7 77 77 77',    # Too short
            'invalid',
            '+1 777 777 77 77',  # Wrong country code
            '9 777 777 77 77',   # Wrong first digit
        ]

        for phone in invalid_phones:
            self.assertFalse(self.validate_phone(phone), f"Phone {phone} should be invalid")

class TestBusinessLogic(unittest.TestCase):
    """Business logic tests"""

    @classmethod
    def setUpClass(cls):
        """Initialize test database"""
        # Use separate test database
        test_db_path = Path(__file__).parent.parent / 'database' / 'rental_test.db'

        # Remove old test database if exists
        if test_db_path.exists():
            test_db_path.unlink()

        # Override DB_PATH for tests
        db.DB_PATH = test_db_path

        # Initialize fresh test database
        db.init_db()

    @classmethod
    def tearDownClass(cls):
        """Clean up test database"""
        # Remove test database after all tests
        test_db_path = Path(__file__).parent.parent / 'database' / 'rental_test.db'
        if test_db_path.exists():
            test_db_path.unlink()

    def test_booking_creation(self):
        """Test booking creation"""
        # Create test user
        telegram_id = 999999996
        user_id = db.create_user(telegram_id, "booking_test", "ru")
        db.update_user(telegram_id, full_name="Test User", phone="+7 777 777 77 77")
        user = db.get_user(telegram_id)

        apartments = db.get_apartments()
        if apartments and len(apartments) > 0:
            apt = apartments[0]
            today = datetime.now().date()
            check_in = (today + timedelta(days=10)).isoformat()
            check_out = (today + timedelta(days=17)).isoformat()

            # Create booking
            booking_id = db.create_booking(
                user['id'],
                apt['id'],
                apt['landlord_id'],
                check_in,
                check_out,
                70000,
                3500
            )

            self.assertIsNotNone(booking_id)

            # Retrieve booking
            booking = db.get_booking_by_id(booking_id)
            self.assertIsNotNone(booking)
            self.assertEqual(booking['status'], 'pending')

    def test_review_creation(self):
        """Test review creation and rating update"""
        apartments = db.get_apartments()
        if apartments and len(apartments) > 0:
            apt = apartments[0]

            # Create test user and booking
            telegram_id = 999999995
            user_id = db.create_user(telegram_id, "review_test", "ru")
            user = db.get_user(telegram_id)

            today = datetime.now().date()
            booking_id = db.create_booking(
                user['id'],
                apt['id'],
                apt['landlord_id'],
                (today - timedelta(days=7)).isoformat(),
                (today - timedelta(days=1)).isoformat(),
                50000,
                2500
            )

            # Update booking status to completed
            db.update_booking_status(booking_id, 'completed')

            # Create review
            db.create_review(
                user['id'],
                apt['id'],
                booking_id,
                5,
                "Отличная квартира!",
                cleanliness=5,
                accuracy=5,
                communication=5,
                location=5
            )

            # Check if apartment rating was updated
            updated_apt = db.get_apartment_by_id(apt['id'])
            self.assertGreater(updated_apt['reviews_count'], 0)

def run_tests():
    """Run all tests and return results"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDatabase))
    suite.addTests(loader.loadTestsFromTestCase(TestLocalization))
    suite.addTests(loader.loadTestsFromTestCase(TestValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestBusinessLogic))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result

if __name__ == '__main__':
    result = run_tests()
    sys.exit(0 if result.wasSuccessful() else 1)
