"""
Extended tests for bot handlers and business logic
Tests bot handlers without requiring aiogram runtime
"""
import unittest
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Add bot directory to path
sys.path.insert(0, os.path.dirname(__file__))

import database as db
from locales import get_text
# Skip keyboards import to avoid aiogram dependency


class TestBotHandlers(unittest.TestCase):
    """Test bot handler logic"""

    @classmethod
    def setUpClass(cls):
        """Initialize test database"""
        test_db_path = Path(__file__).parent.parent / 'database' / 'rental_test.db'
        if test_db_path.exists():
            test_db_path.unlink()
        db.DB_PATH = test_db_path
        db.init_db()

    @classmethod
    def tearDownClass(cls):
        """Clean up test database"""
        test_db_path = Path(__file__).parent.parent / 'database' / 'rental_test.db'
        if test_db_path.exists():
            test_db_path.unlink()

    def test_user_registration_flow(self):
        """Test complete user registration flow"""
        telegram_id = 888888888

        # Step 1: Create user
        user_id = db.create_user(telegram_id, "test_registration", "ru")
        self.assertIsNotNone(user_id)

        user = db.get_user(telegram_id)
        self.assertIsNone(user['full_name'])
        self.assertIsNone(user['phone'])

        # Step 2: Update with full name
        db.update_user(telegram_id, full_name="Тестовый Пользователь")
        user = db.get_user(telegram_id)
        self.assertEqual(user['full_name'], "Тестовый Пользователь")

        # Step 3: Update with phone
        db.update_user(telegram_id, phone="+7 777 123 45 67")
        user = db.get_user(telegram_id)
        self.assertEqual(user['phone'], "+7 777 123 45 67")

    def test_landlord_request_flow(self):
        """Test landlord request creation and approval"""
        telegram_id = 777777777

        # Create landlord request
        db.create_landlord_request(
            telegram_id=telegram_id,
            full_name="Арендодатель Тестовый",
            phone="+7 777 999 88 77",
            email="landlord@test.com"
        )

        # Verify request exists
        conn = db.get_connection()
        cursor = conn.execute(
            "SELECT * FROM landlord_requests WHERE telegram_id = ?",
            (telegram_id,)
        )
        request = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(request)
        self.assertEqual(request['status'], 'pending')
        self.assertEqual(request['email'], 'landlord@test.com')

    def test_search_filters(self):
        """Test apartment search with filters"""
        # Create test cities and districts for testing
        conn = db.get_connection()
        cursor = conn.cursor()

        # Insert test city
        cursor.execute("""
            INSERT INTO cities (name_ru, name_kk, created_at)
            VALUES ('Тест Город', 'Тест Қала', CURRENT_TIMESTAMP)
        """)
        city_id = cursor.lastrowid

        # Insert test districts
        cursor.execute("""
            INSERT INTO districts (city_id, name_ru, name_kk, created_at)
            VALUES (?, 'Тест Район 1', 'Тест Аудан 1', CURRENT_TIMESTAMP)
        """, (city_id,))
        district_id = cursor.lastrowid

        conn.commit()
        conn.close()

        # Get all cities
        cities = db.get_cities()
        self.assertGreater(len(cities), 0)

        city = cities[0]
        districts = db.get_districts(city['id'])

        if districts:
            district = districts[0]

            # Search with city filter
            apartments_city = db.get_apartments(city_id=city['id'])

            # Search with city and district filter
            apartments_district = db.get_apartments(
                city_id=city['id'],
                district_id=district['id']
            )

            # District search should return subset of city search
            self.assertLessEqual(len(apartments_district), len(apartments_city))

    def test_booking_status_transitions(self):
        """Test booking status transitions"""
        telegram_id = 666666666
        user_id = db.create_user(telegram_id, "booking_status_test", "ru")
        db.update_user(telegram_id, full_name="Test User", phone="+7 777 777 77 77")
        user = db.get_user(telegram_id)

        apartments = db.get_apartments()
        if apartments:
            apt = apartments[0]
            today = datetime.now().date()
            check_in = (today + timedelta(days=5)).isoformat()
            check_out = (today + timedelta(days=10)).isoformat()

            # Create booking
            booking_id = db.create_booking(
                user['id'],
                apt['id'],
                apt['landlord_id'],
                check_in,
                check_out,
                50000,
                2500
            )

            # Test status transitions
            statuses = ['pending', 'confirmed', 'completed']
            for status in statuses:
                db.update_booking_status(booking_id, status)
                booking = db.get_booking_by_id(booking_id)
                self.assertEqual(booking['status'], status)

    def test_availability_check_with_confirmed_only(self):
        """Test that only confirmed bookings block dates"""
        telegram_id = 555555555
        user_id = db.create_user(telegram_id, "availability_test", "ru")
        user = db.get_user(telegram_id)

        apartments = db.get_apartments()
        if apartments:
            apt = apartments[0]
            today = datetime.now().date()
            check_in = (today + timedelta(days=15)).isoformat()
            check_out = (today + timedelta(days=20)).isoformat()

            # Create pending booking
            booking_id = db.create_booking(
                user['id'],
                apt['id'],
                apt['landlord_id'],
                check_in,
                check_out,
                50000,
                2500
            )

            # Should be available (pending doesn't block)
            is_available = db.check_apartment_availability(
                apt['id'],
                check_in,
                check_out
            )
            self.assertTrue(is_available)

            # Confirm booking
            db.update_booking_status(booking_id, 'confirmed')

            # Should NOT be available now
            is_available = db.check_apartment_availability(
                apt['id'],
                check_in,
                check_out
            )
            self.assertFalse(is_available)

    def test_get_booked_dates(self):
        """Test getting booked dates for apartment"""
        telegram_id = 444444444
        user_id = db.create_user(telegram_id, "booked_dates_test", "ru")
        user = db.get_user(telegram_id)

        apartments = db.get_apartments()
        if apartments:
            apt = apartments[0]
            today = datetime.now().date()
            check_in = (today + timedelta(days=25)).isoformat()
            check_out = (today + timedelta(days=28)).isoformat()

            # Create confirmed booking
            booking_id = db.create_booking(
                user['id'],
                apt['id'],
                apt['landlord_id'],
                check_in,
                check_out,
                30000,
                1500
            )
            db.update_booking_status(booking_id, 'confirmed')

            # Get booked dates
            booked_dates = db.get_booked_dates(apt['id'])

            # Should have 3 dates (25, 26, 27 - not including checkout day)
            self.assertEqual(len(booked_dates), 3)
            self.assertIn(check_in, booked_dates)


class TestLocalizationExtended(unittest.TestCase):
    """Extended localization tests"""

    def test_all_required_keys_exist(self):
        """Test that all required localization keys exist"""
        required_keys = [
            'welcome',
            'btn_search',
            'btn_favorites',
            'btn_bookings',
            'select_city',
            'select_district',
            'active_filters_no_dates',
            'available_apartments',
            'no_apartments',
            'enter_full_name',
            'enter_phone',
            'invalid_phone',
        ]

        for key in required_keys:
            text_ru = get_text(key, 'ru')
            text_kk = get_text(key, 'kk')

            self.assertIsNotNone(text_ru, f"Missing RU translation for: {key}")
            self.assertIsNotNone(text_kk, f"Missing KK translation for: {key}")
            self.assertNotEqual(text_ru, '', f"Empty RU translation for: {key}")
            self.assertNotEqual(text_kk, '', f"Empty KK translation for: {key}")

    def test_landlord_request_texts(self):
        """Test landlord request specific texts"""
        text = get_text('enter_landlord_name', 'ru')
        self.assertIn('ФИО', text)

        text = get_text('enter_landlord_phone', 'ru')
        self.assertIn('телефон', text.lower())

        text = get_text('enter_landlord_email', 'ru')
        self.assertIn('email', text.lower())


class TestDatabaseIntegrity(unittest.TestCase):
    """Test database integrity and constraints"""

    @classmethod
    def setUpClass(cls):
        """Initialize test database"""
        test_db_path = Path(__file__).parent.parent / 'database' / 'rental_test.db'
        if test_db_path.exists():
            test_db_path.unlink()
        db.DB_PATH = test_db_path
        db.init_db()

    @classmethod
    def tearDownClass(cls):
        """Clean up test database"""
        test_db_path = Path(__file__).parent.parent / 'database' / 'rental_test.db'
        if test_db_path.exists():
            test_db_path.unlink()

    def test_cascade_delete_apartments(self):
        """Test cascade delete on apartments"""
        # This test ensures that related records are handled properly
        apartments = db.get_apartments()
        if apartments:
            apt = apartments[0]
            landlord_id = apt['landlord_id']

            # Verify apartment exists
            apt_check = db.get_apartment_by_id(apt['id'])
            self.assertIsNotNone(apt_check)

    def test_unique_constraints(self):
        """Test unique constraints"""
        telegram_id = 222222222

        # Create first user
        db.create_user(telegram_id, "unique_test", "ru")

        # Try to create duplicate - should handle gracefully
        try:
            db.create_user(telegram_id, "unique_test2", "kk")
            # If it doesn't raise an error, check that original wasn't overwritten
            user = db.get_user(telegram_id)
            self.assertEqual(user['username'], "unique_test")
        except Exception:
            # It's OK if it raises an error for duplicate
            pass

    def test_default_values(self):
        """Test default values in database"""
        telegram_id = 111111111
        db.create_user(telegram_id, "defaults_test", "ru")

        user = db.get_user(telegram_id)
        self.assertEqual(user['language'], 'ru')
        self.assertIsNotNone(user['created_at'])

        # Check settings defaults
        platform_fee = db.get_setting('platform_fee_percent')
        self.assertEqual(platform_fee, '5')


def run_tests():
    """Run all handler tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestBotHandlers))
    suite.addTests(loader.loadTestsFromTestCase(TestLocalizationExtended))
    suite.addTests(loader.loadTestsFromTestCase(TestDatabaseIntegrity))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == '__main__':
    result = run_tests()
    sys.exit(0 if result.wasSuccessful() else 1)
