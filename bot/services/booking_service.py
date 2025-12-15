"""
Booking service - business logic for bookings
"""
from datetime import datetime
from typing import Tuple, Optional, Dict, Any

import database as db
from constants import MIN_BOOKING_DAYS


class BookingService:
    """Service for booking-related business logic"""

    @staticmethod
    def calculate_booking_price(
        apartment_id: int,
        user_id: int,
        check_in: str,
        check_out: str
    ) -> Tuple[float, float, int, bool, int]:
        """
        Calculate booking price with promotions

        Returns:
            Tuple of (total_price, original_price, days, has_discount, discount_days)
        """
        apartment = db.get_apartment_by_id(apartment_id)
        if not apartment:
            raise ValueError("Apartment not found")

        check_in_date = datetime.strptime(check_in, "%Y-%m-%d")
        check_out_date = datetime.strptime(check_out, "%Y-%m-%d")
        days = (check_out_date - check_in_date).days

        if days < MIN_BOOKING_DAYS:
            raise ValueError(f"Minimum booking duration is {MIN_BOOKING_DAYS} day(s)")

        original_price = apartment['price_per_day'] * days

        # Check for promotion benefit
        should_apply_bonus, free_days, _ = db.calculate_promotion_benefit(
            user_id, apartment_id, days
        )

        discount_days = free_days if should_apply_bonus else 0
        paid_days = days - discount_days
        total_price = apartment['price_per_day'] * paid_days

        return total_price, original_price, days, should_apply_bonus, discount_days

    @staticmethod
    def validate_booking_dates(check_in: str, check_out: str) -> Tuple[bool, str]:
        """
        Validate booking dates

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            check_in_date = datetime.strptime(check_in, "%Y-%m-%d").date()
            check_out_date = datetime.strptime(check_out, "%Y-%m-%d").date()
        except ValueError:
            return False, "Invalid date format"

        today = datetime.now().date()

        if check_in_date < today:
            return False, "Check-in date cannot be in the past"

        if check_out_date <= check_in_date:
            return False, "Check-out date must be after check-in date"

        days = (check_out_date - check_in_date).days
        if days < MIN_BOOKING_DAYS:
            return False, f"Minimum booking duration is {MIN_BOOKING_DAYS} day(s)"

        return True, ""

    @staticmethod
    def check_availability(apartment_id: int, check_in: str, check_out: str) -> bool:
        """Check if apartment is available for given dates"""
        return db.check_apartment_availability(apartment_id, check_in, check_out)

    @staticmethod
    def get_platform_fee(total_price: float, landlord_id: int = None) -> float:
        """Calculate platform fee
        
        If landlord is an admin and charge_fee_for_admins setting is '0',
        returns 0 (no fee charged for admin apartments).
        """
        # Check if we should skip fee for admin landlords
        if landlord_id:
            charge_for_admins = db.get_setting('charge_fee_for_admins') or '0'
            if charge_for_admins == '0':
                landlord = db.get_user_by_id(landlord_id)
                if landlord and landlord.get('roles'):
                    import json
                    try:
                        roles = json.loads(landlord['roles']) if isinstance(landlord['roles'], str) else landlord['roles']
                        if 'admin' in roles:
                            return 0.0
                    except (json.JSONDecodeError, TypeError):
                        pass
        
        fee_percent = float(db.get_setting('platform_fee_percent') or 5)
        return total_price * (fee_percent / 100)
