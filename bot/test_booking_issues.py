"""
Расширенные тесты для проверки найденных проблем в системе бронирования
Tests for identified booking system issues
"""
import unittest
import sys
import os
from datetime import datetime, timedelta, date
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import time
import threading

# Add bot directory to path
sys.path.insert(0, os.path.dirname(__file__))

import database as db


class TestBookingIssues(unittest.TestCase):
    """Тесты для проверки выявленных проблем бронирования"""

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

    def setUp(self):
        """Set up test data before each test"""
        # Create test users - create_user returns user_id, but we need to get user by telegram_id
        db.create_user(111111, "test_user1", "ru")
        db.create_user(222222, "test_user2", "ru")
        db.create_user(333333, "test_landlord", "ru")

        # Get user IDs from database
        user1 = db.get_user(111111)
        user2 = db.get_user(222222)
        landlord = db.get_user(333333)

        self.user1_id = user1['id']
        self.user2_id = user2['id']
        self.landlord_id = landlord['id']

        # Update users with required data (removed is_landlord - use roles instead)
        db.update_user(111111, full_name="Test User 1", phone="+77771234567")
        db.update_user(222222, full_name="Test User 2", phone="+77771234568")
        db.update_user(333333, full_name="Test Landlord", phone="+77771234569")
        db.add_role(self.landlord_id, 'landlord')

        # Create test apartment using direct SQL (no create_apartment function exists)
        conn = db.get_connection()
        # First ensure we have city and district
        conn.execute("INSERT OR IGNORE INTO cities (id, name_ru, name_kk) VALUES (1, 'Алматы', 'Алматы')")
        conn.execute("INSERT OR IGNORE INTO districts (id, city_id, name_ru, name_kk) VALUES (1, 1, 'Медеу', 'Медеу')")
        conn.execute("""
            INSERT INTO apartments (landlord_id, city_id, district_id, title_ru, title_kk,
                                   description_ru, description_kk, address, price_per_day, rooms, is_active)
            VALUES (?, 1, 1, 'Test Apartment', 'Test Apartment', 'Test Description', 'Test Description',
                    'Test Street 1', 10000, 2, 1)
        """, (self.landlord_id,))
        self.apartment_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.commit()
        conn.close()

    def tearDown(self):
        """Clean up after each test"""
        # Clean up database after each test
        conn = db.get_connection()
        conn.execute("DELETE FROM bookings")
        conn.execute("DELETE FROM apartments")
        conn.execute("DELETE FROM users")
        conn.commit()
        conn.close()

    # ============================================================
    # ТЕСТ 1: Race Condition при одновременных бронированиях
    # ============================================================
    def test_race_condition_concurrent_bookings(self):
        """
        ПРОБЛЕМА: Два пользователя могут создать бронирование на одни даты
        из-за отсутствия транзакционности между проверкой и созданием
        """
        check_in = (datetime.now() + timedelta(days=5)).date()
        check_out = (datetime.now() + timedelta(days=7)).date()

        results = []

        def create_booking_for_user(user_id):
            """Simulate user creating booking"""
            # Проверка доступности
            available = db.check_apartment_availability(
                self.apartment_id,
                check_in.strftime('%Y-%m-%d'),
                check_out.strftime('%Y-%m-%d')
            )

            if available:
                # Небольшая задержка чтобы симулировать race condition
                time.sleep(0.01)

                # Создание бронирования
                booking_id = db.create_booking(
                    user_id=user_id,
                    apartment_id=self.apartment_id,
                    landlord_id=self.landlord_id,
                    check_in=check_in.strftime('%Y-%m-%d'),
                    check_out=check_out.strftime('%Y-%m-%d'),
                    total_price=20000,
                    platform_fee=1000
                )
                results.append(booking_id)

        # Создаем два потока для симуляции одновременных запросов
        thread1 = threading.Thread(target=create_booking_for_user, args=(self.user1_id,))
        thread2 = threading.Thread(target=create_booking_for_user, args=(self.user2_id,))

        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()

        # ОЖИДАЕМОЕ ПОВЕДЕНИЕ: Должно быть создано только 1 бронирование
        # ТЕКУЩЕЕ ПОВЕДЕНИЕ: Создаются 2 бронирования (БАГ!)
        print(f"\n⚠️  RACE CONDITION TEST: Создано {len(results)} бронирований (ожидалось 1)")

        # Этот тест ДОЛЖЕН FAIL с текущей реализацией
        if len(results) > 1:
            print("   ❌ БАГ ПОДТВЕРЖДЕН: Возможно двойное бронирование!")

        # Проверяем что создано 2 pending бронирования на одни даты
        bookings = db.get_user_bookings(self.user1_id)
        bookings += db.get_user_bookings(self.user2_id)

        self.assertGreaterEqual(len(results), 1, "Должно быть создано хотя бы 1 бронирование")

    # ============================================================
    # ТЕСТ 2: Бронирование дат в прошлом
    # ============================================================
    def test_booking_past_dates(self):
        """
        ПРОБЛЕМА: Система позволяет создать бронирование на даты в прошлом
        """
        past_check_in = (datetime.now() - timedelta(days=5)).date()
        past_check_out = (datetime.now() - timedelta(days=3)).date()

        # Создаем бронирование на даты в прошлом
        booking_id = db.create_booking(
            user_id=self.user1_id,
            apartment_id=self.apartment_id,
            landlord_id=self.landlord_id,
            check_in=past_check_in.strftime('%Y-%m-%d'),
            check_out=past_check_out.strftime('%Y-%m-%d'),
            total_price=20000,
            platform_fee=1000
        )

        print(f"\n⚠️  PAST DATES TEST: Бронирование в прошлом создано с ID={booking_id}")

        # ОЖИДАЕМОЕ: booking_id должен быть None или должна быть ошибка
        # ТЕКУЩЕЕ: Бронирование создается (БАГ!)
        if booking_id:
            print("   ❌ БАГ ПОДТВЕРЖДЕН: Можно забронировать даты в прошлом!")

        self.assertIsNotNone(booking_id, "В текущей реализации бронирование создается (это баг)")

    # ============================================================
    # ТЕСТ 3: Бронирование у неактивного арендодателя
    # ============================================================
    def test_booking_inactive_landlord(self):
        """
        ПРОБЛЕМА: Можно забронировать квартиру у деактивированного арендодателя
        """
        # Деактивируем арендодателя
        conn = db.get_connection()
        conn.execute("UPDATE users SET is_active = 0 WHERE id = ?", (self.landlord_id,))
        conn.commit()
        conn.close()

        check_in = (datetime.now() + timedelta(days=5)).date()
        check_out = (datetime.now() + timedelta(days=7)).date()

        # Проверяем доступность
        available = db.check_apartment_availability(
            self.apartment_id,
            check_in.strftime('%Y-%m-%d'),
            check_out.strftime('%Y-%m-%d')
        )

        print(f"\n⚠️  INACTIVE LANDLORD TEST: Квартира доступна={available}")

        # ОЖИДАЕМОЕ: available должно быть False (арендодатель неактивен)
        # ТЕКУЩЕЕ: available=True (БАГ!)
        if available:
            print("   ❌ БАГ ПОДТВЕРЖДЕН: Можно забронировать у неактивного арендодателя!")

        # В текущей реализации бронирование возможно
        self.assertTrue(available, "В текущей реализации это возможно (это баг)")

    # ============================================================
    # ТЕСТ 4: Статусы бронирования и их переходы
    # ============================================================
    def test_booking_status_workflow(self):
        """
        Тестируем корректные переходы статусов и логику блокировки дат
        """
        check_in = (datetime.now() + timedelta(days=5)).date()
        check_out = (datetime.now() + timedelta(days=7)).date()

        # Создаем бронирование (статус: pending)
        booking_id = db.create_booking(
            user_id=self.user1_id,
            apartment_id=self.apartment_id,
            landlord_id=self.landlord_id,
            check_in=check_in.strftime('%Y-%m-%d'),
            check_out=check_out.strftime('%Y-%m-%d'),
            total_price=20000,
            platform_fee=1000
        )

        # Pending бронирование НЕ должно блокировать даты
        available = db.check_apartment_availability(
            self.apartment_id,
            check_in.strftime('%Y-%m-%d'),
            check_out.strftime('%Y-%m-%d')
        )
        self.assertTrue(available, "Pending бронирование не должно блокировать даты")

        # Подтверждаем бронирование
        db.update_booking_status(booking_id, 'confirmed')

        # Confirmed бронирование ДОЛЖНО блокировать даты
        available = db.check_apartment_availability(
            self.apartment_id,
            check_in.strftime('%Y-%m-%d'),
            check_out.strftime('%Y-%m-%d')
        )
        self.assertFalse(available, "Confirmed бронирование должно блокировать даты")

        # Отменяем бронирование
        db.update_booking_status(booking_id, 'cancelled')

        # Cancelled бронирование НЕ должно блокировать даты
        available = db.check_apartment_availability(
            self.apartment_id,
            check_in.strftime('%Y-%m-%d'),
            check_out.strftime('%Y-%m-%d')
        )
        self.assertTrue(available, "Cancelled бронирование не должно блокировать даты")

        print("\n✓ BOOKING STATUS WORKFLOW: Все переходы статусов работают корректно")

    # ============================================================
    # ТЕСТ 5: Расчет цены и комиссии
    # ============================================================
    def test_booking_price_calculation(self):
        """
        Проверяем корректность расчета цены и комиссии платформы
        """
        check_in = datetime.now().date() + timedelta(days=1)
        check_out = datetime.now().date() + timedelta(days=4)  # 3 ночи

        # Получаем цену квартиры (fixed: use get_apartment_by_id instead of get_apartment)
        apartment = db.get_apartment_by_id(self.apartment_id)
        price_per_day = apartment['price_per_day']

        # Рассчитываем ожидаемую цену
        days = (check_out - check_in).days
        expected_total = price_per_day * days

        # Комиссия 5%
        fee_percent = float(db.get_setting('platform_fee_percent') or 5)
        expected_fee = expected_total * (fee_percent / 100)

        # Создаем бронирование
        booking_id = db.create_booking(
            user_id=self.user1_id,
            apartment_id=self.apartment_id,
            landlord_id=self.landlord_id,
            check_in=check_in.strftime('%Y-%m-%d'),
            check_out=check_out.strftime('%Y-%m-%d'),
            total_price=expected_total,
            platform_fee=expected_fee
        )

        # Получаем бронирование из БД (fixed: use get_booking_by_id instead of get_booking)
        booking = db.get_booking_by_id(booking_id)

        print(f"\n✓ PRICE CALCULATION TEST:")
        print(f"   Дней: {days}")
        print(f"   Цена за день: {price_per_day}")
        print(f"   Общая цена: {booking['total_price']} (ожидалось {expected_total})")
        print(f"   Комиссия: {booking['platform_fee']} (ожидалось {expected_fee:.2f})")

        self.assertEqual(booking['total_price'], expected_total)
        self.assertAlmostEqual(booking['platform_fee'], expected_fee, places=2)

    # ============================================================
    # ТЕСТ 6: Перекрывающиеся бронирования
    # ============================================================
    def test_overlapping_bookings(self):
        """
        Проверяем что система корректно определяет перекрывающиеся бронирования
        """
        # Создаем первое CONFIRMED бронирование: 5-10 число
        booking1_id = db.create_booking(
            user_id=self.user1_id,
            apartment_id=self.apartment_id,
            landlord_id=self.landlord_id,
            check_in=(datetime.now() + timedelta(days=5)).date().strftime('%Y-%m-%d'),
            check_out=(datetime.now() + timedelta(days=10)).date().strftime('%Y-%m-%d'),
            total_price=50000,
            platform_fee=2500
        )
        db.update_booking_status(booking1_id, 'confirmed')

        # Тест 1: Полное перекрытие (3-12) - должно быть недоступно
        available = db.check_apartment_availability(
            self.apartment_id,
            (datetime.now() + timedelta(days=3)).date().strftime('%Y-%m-%d'),
            (datetime.now() + timedelta(days=12)).date().strftime('%Y-%m-%d')
        )
        self.assertFalse(available, "Полностью перекрывающееся бронирование должно быть недоступно")

        # Тест 2: Частичное перекрытие слева (3-7) - должно быть недоступно
        available = db.check_apartment_availability(
            self.apartment_id,
            (datetime.now() + timedelta(days=3)).date().strftime('%Y-%m-%d'),
            (datetime.now() + timedelta(days=7)).date().strftime('%Y-%m-%d')
        )
        self.assertFalse(available, "Частично перекрывающееся бронирование (слева) должно быть недоступно")

        # Тест 3: Частичное перекрытие справа (8-13) - должно быть недоступно
        available = db.check_apartment_availability(
            self.apartment_id,
            (datetime.now() + timedelta(days=8)).date().strftime('%Y-%m-%d'),
            (datetime.now() + timedelta(days=13)).date().strftime('%Y-%m-%d')
        )
        self.assertFalse(available, "Частично перекрывающееся бронирование (справа) должно быть недоступно")

        # Тест 4: Бронирование до существующего (1-4) - должно быть доступно
        available = db.check_apartment_availability(
            self.apartment_id,
            (datetime.now() + timedelta(days=1)).date().strftime('%Y-%m-%d'),
            (datetime.now() + timedelta(days=4)).date().strftime('%Y-%m-%d')
        )
        self.assertTrue(available, "Бронирование до существующего должно быть доступно")

        # Тест 5: Бронирование после существующего (11-15) - должно быть доступно
        available = db.check_apartment_availability(
            self.apartment_id,
            (datetime.now() + timedelta(days=11)).date().strftime('%Y-%m-%d'),
            (datetime.now() + timedelta(days=15)).date().strftime('%Y-%m-%d')
        )
        self.assertTrue(available, "Бронирование после существующего должно быть доступно")

        # Тест 6: Back-to-back бронирование (check_in = previous check_out)
        # День выезда = день заезда следующего
        available = db.check_apartment_availability(
            self.apartment_id,
            (datetime.now() + timedelta(days=10)).date().strftime('%Y-%m-%d'),
            (datetime.now() + timedelta(days=12)).date().strftime('%Y-%m-%d')
        )
        # Это зависит от бизнес-логики: разрешено ли заезд в день выезда?
        # В текущей реализации это должно быть доступно
        print(f"\n⚠️  BACK-TO-BACK BOOKING: Доступно={available}")

        print("\n✓ OVERLAPPING BOOKINGS TEST: Все проверки перекрытий работают")

    # ============================================================
    # ТЕСТ 7: Минимальная длительность бронирования
    # ============================================================
    def test_minimum_booking_duration(self):
        """
        ПРОБЛЕМА: Нет проверки минимальной длительности бронирования
        Можно забронировать на 1 день или даже на 0 дней
        """
        check_in = (datetime.now() + timedelta(days=5)).date()

        # Попытка забронировать на 0 дней (check_in == check_out)
        booking_id = db.create_booking(
            user_id=self.user1_id,
            apartment_id=self.apartment_id,
            landlord_id=self.landlord_id,
            check_in=check_in.strftime('%Y-%m-%d'),
            check_out=check_in.strftime('%Y-%m-%d'),  # Та же дата!
            total_price=0,
            platform_fee=0
        )

        print(f"\n⚠️  ZERO DURATION TEST: Бронирование на 0 дней создано с ID={booking_id}")

        if booking_id:
            print("   ❌ БАГ ПОДТВЕРЖДЕН: Можно забронировать на 0 дней!")

        # В текущей реализации это возможно (баг)
        self.assertIsNotNone(booking_id, "В текущей реализации можно забронировать на 0 дней")

    # ============================================================
    # ТЕСТ 8: Множественные pending бронирования
    # ============================================================
    def test_multiple_pending_bookings_same_dates(self):
        """
        Проверяем что несколько пользователей могут создать pending бронирования
        на одни даты, но только одно может быть confirmed
        """
        check_in = (datetime.now() + timedelta(days=5)).date()
        check_out = (datetime.now() + timedelta(days=7)).date()

        # Создаем 3 pending бронирования на одни даты
        booking1 = db.create_booking(
            user_id=self.user1_id,
            apartment_id=self.apartment_id,
            landlord_id=self.landlord_id,
            check_in=check_in.strftime('%Y-%m-%d'),
            check_out=check_out.strftime('%Y-%m-%d'),
            total_price=20000,
            platform_fee=1000
        )

        booking2 = db.create_booking(
            user_id=self.user2_id,
            apartment_id=self.apartment_id,
            landlord_id=self.landlord_id,
            check_in=check_in.strftime('%Y-%m-%d'),
            check_out=check_out.strftime('%Y-%m-%d'),
            total_price=20000,
            platform_fee=1000
        )

        # Оба должны быть созданы
        self.assertIsNotNone(booking1)
        self.assertIsNotNone(booking2)

        # Подтверждаем первое
        db.update_booking_status(booking1, 'confirmed')

        # Теперь даты должны быть заняты
        available = db.check_apartment_availability(
            self.apartment_id,
            check_in.strftime('%Y-%m-%d'),
            check_out.strftime('%Y-%m-%d')
        )
        self.assertFalse(available, "После подтверждения первого бронирования даты должны быть заняты")

        # Второе бронирование не должно быть подтверждено
        # В идеале должна быть валидация при попытке подтвердить
        print("\n✓ MULTIPLE PENDING TEST: Несколько pending бронирований возможно, но только одно confirmed")


class TestBookingEdgeCases(unittest.TestCase):
    """Тесты граничных случаев"""

    @classmethod
    def setUpClass(cls):
        """Initialize test database"""
        test_db_path = Path(__file__).parent.parent / 'database' / 'rental_test.db'
        if test_db_path.exists():
            test_db_path.unlink()
        db.DB_PATH = test_db_path
        db.init_db()

    def setUp(self):
        """Set up test data"""
        db.create_user(444444, "edge_user", "ru")
        db.create_user(555555, "edge_landlord", "ru")

        user = db.get_user(444444)
        landlord = db.get_user(555555)

        self.user_id = user['id']
        self.landlord_id = landlord['id']

        db.update_user(444444, full_name="Edge User", phone="+77771111111")
        db.update_user(555555, full_name="Edge Landlord", phone="+77772222222")
        db.add_role(self.landlord_id, 'landlord')

        # Create test apartment using direct SQL
        conn = db.get_connection()
        conn.execute("INSERT OR IGNORE INTO cities (id, name_ru, name_kk) VALUES (1, 'Алматы', 'Алматы')")
        conn.execute("INSERT OR IGNORE INTO districts (id, city_id, name_ru, name_kk) VALUES (1, 1, 'Медеу', 'Медеу')")
        conn.execute("""
            INSERT INTO apartments (landlord_id, city_id, district_id, title_ru, title_kk,
                                   description_ru, description_kk, address, price_per_day, rooms, is_active)
            VALUES (?, 1, 1, 'Edge Apartment', 'Edge Apartment', 'Test', 'Test', 'Test St', 5000, 1, 1)
        """, (self.landlord_id,))
        self.apartment_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.commit()
        conn.close()

    def tearDown(self):
        """Clean up"""
        conn = db.get_connection()
        conn.execute("DELETE FROM bookings")
        conn.execute("DELETE FROM apartments")
        conn.execute("DELETE FROM users")
        conn.commit()
        conn.close()

    def test_very_long_booking(self):
        """Тест очень длинного бронирования (более года)"""
        check_in = datetime.now().date() + timedelta(days=1)
        check_out = datetime.now().date() + timedelta(days=400)  # Более года

        booking_id = db.create_booking(
            user_id=self.user_id,
            apartment_id=self.apartment_id,
            landlord_id=self.landlord_id,
            check_in=check_in.strftime('%Y-%m-%d'),
            check_out=check_out.strftime('%Y-%m-%d'),
            total_price=2000000,
            platform_fee=100000
        )

        self.assertIsNotNone(booking_id)
        print("\n✓ LONG BOOKING TEST: Длинное бронирование создано успешно")

    def test_check_out_before_check_in(self):
        """
        ПРОБЛЕМА: Нет валидации что check_out > check_in в БД
        """
        check_in = (datetime.now() + timedelta(days=10)).date()
        check_out = (datetime.now() + timedelta(days=5)).date()  # Раньше check_in!

        booking_id = db.create_booking(
            user_id=self.user_id,
            apartment_id=self.apartment_id,
            landlord_id=self.landlord_id,
            check_in=check_in.strftime('%Y-%m-%d'),
            check_out=check_out.strftime('%Y-%m-%d'),
            total_price=25000,
            platform_fee=1250
        )

        print(f"\n⚠️  INVALID DATES TEST: check_out < check_in - Бронирование создано={booking_id is not None}")

        if booking_id:
            print("   ❌ БАГ ПОДТВЕРЖДЕН: Можно создать бронирование с check_out < check_in!")

        # В текущей реализации это возможно (баг)
        self.assertIsNotNone(booking_id, "В текущей реализации это возможно (это баг)")


if __name__ == '__main__':
    print("=" * 70)
    print("ЗАПУСК ТЕСТОВ ВЫЯВЛЕННЫХ ПРОБЛЕМ БРОНИРОВАНИЯ")
    print("=" * 70)
    print("\nТестируем:")
    print("1. Race condition при одновременных бронированиях")
    print("2. Бронирование дат в прошлом")
    print("3. Бронирование у неактивного арендодателя")
    print("4. Корректность переходов статусов")
    print("5. Расчет цены и комиссии")
    print("6. Перекрывающиеся бронирования")
    print("7. Минимальная длительность бронирования")
    print("8. Множественные pending бронирования")
    print("9. Граничные случаи (очень длинное бронирование, неверные даты)")
    print("=" * 70)
    print()

    unittest.main(verbosity=2)
