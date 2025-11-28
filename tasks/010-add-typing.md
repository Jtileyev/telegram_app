# Задача 010: Добавить типизацию

## Приоритет: 🟢 Низкий

## Описание
Использовать TypedDict для словарей из БД вместо `Dict[str, Any]`.

## Решение

### Создать bot/types.py
```python
from typing import TypedDict, Optional, List
from datetime import datetime


class User(TypedDict):
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


class Apartment(TypedDict):
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
    promotion_bookings_required: Optional[int]
    promotion_free_days: Optional[int]


class Booking(TypedDict):
    id: int
    user_id: int
    apartment_id: int
    landlord_id: int
    check_in_date: str
    check_out_date: str
    total_price: float
    platform_fee: float
    status: str
    promotion_id: Optional[int]
    promotion_discount_days: int
    original_price: Optional[float]
    created_at: str
    updated_at: str


class Review(TypedDict):
    id: int
    user_id: int
    apartment_id: int
    booking_id: int
    rating: int
    comment: Optional[str]
    helpful_count: int
    not_helpful_count: int
    user_name: str
    created_at: str
```

### Использовать в database.py
```python
from types import User, Apartment, Booking

def get_user(telegram_id: int) -> Optional[User]:
    ...

def get_apartment_by_id(apartment_id: int) -> Optional[Apartment]:
    ...
```

## Проверка
- [ ] Все функции БД имеют типизированные возвращаемые значения
- [ ] IDE показывает автодополнение для полей словарей
- [ ] mypy не выдаёт ошибок
