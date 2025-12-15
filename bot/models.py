"""
Type definitions for database entities
"""
from typing import TypedDict, Optional, List


class User(TypedDict, total=False):
    """User entity from database"""
    id: int
    telegram_id: int
    email: Optional[str]
    username: Optional[str]
    full_name: Optional[str]
    phone: Optional[str]
    language: str
    roles: str  # JSON array
    is_active: bool
    created_at: str
    updated_at: str


class City(TypedDict):
    """City entity"""
    id: int
    name_ru: str
    name_kk: str


class District(TypedDict):
    """District entity"""
    id: int
    city_id: int
    name_ru: str
    name_kk: str


class Apartment(TypedDict, total=False):
    """Apartment entity with joined fields"""
    id: int
    landlord_id: int
    city_id: int
    district_id: int
    title_ru: str
    title_kk: str
    description_ru: Optional[str]
    description_kk: Optional[str]
    address: str
    price_per_day: float
    price_per_month: Optional[float]
    gis_link: Optional[str]
    amenities: List[str]
    photos: List[str]
    promotion_id: Optional[int]
    rating: float
    reviews_count: int
    is_active: bool
    # Joined fields
    landlord_phone: Optional[str]
    landlord_name: Optional[str]
    landlord_telegram_id: Optional[int]
    city_name_ru: str
    city_name_kk: str
    district_name_ru: str
    district_name_kk: str
    promotion_name: Optional[str]
    promotion_description: Optional[str]
    promotion_bookings_required: Optional[int]
    promotion_free_days: Optional[int]
    promotion_active: Optional[bool]


class Booking(TypedDict, total=False):
    """Booking entity with joined fields"""
    id: int
    user_id: int
    apartment_id: int
    landlord_id: int
    check_in_date: str
    check_out_date: str
    total_price: float
    platform_fee: float
    status: str  # pending, confirmed, completed, rejected, cancelled
    promotion_id: Optional[int]
    promotion_discount_days: int
    original_price: Optional[float]
    created_at: str
    updated_at: str
    # Joined fields
    title_ru: str
    title_kk: str
    address: str
    price_per_day: float
    landlord_phone: Optional[str]
    landlord_name: Optional[str]
    landlord_telegram_id: Optional[int]
    user_telegram_id: Optional[int]
    user_name: Optional[str]
    user_phone: Optional[str]


class Review(TypedDict, total=False):
    """Review entity with joined fields"""
    id: int
    user_id: int
    apartment_id: int
    booking_id: int
    rating: int
    comment: Optional[str]
    cleanliness_rating: Optional[int]
    accuracy_rating: Optional[int]
    communication_rating: Optional[int]
    location_rating: Optional[int]
    helpful_count: int
    not_helpful_count: int
    is_visible: bool
    created_at: str
    # Joined fields
    user_name: str


class Promotion(TypedDict, total=False):
    """Promotion entity"""
    id: int
    name: str
    description: str
    bookings_required: int
    free_days: int
    is_active: bool
    created_at: str
    updated_at: str


class UserPromotionProgress(TypedDict, total=False):
    """User promotion progress entity"""
    id: int
    user_id: int
    apartment_id: int
    promotion_id: int
    bookings_count: int
    created_at: str
    updated_at: str
    # Joined fields
    bookings_required: int
    free_days: int
    promotion_name: str


class LandlordRequest(TypedDict, total=False):
    """Landlord connection request"""
    id: int
    telegram_id: int
    full_name: str
    phone: str
    email: str
    status: str
    created_at: str
