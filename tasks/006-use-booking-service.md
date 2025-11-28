# Задача 006: Использовать BookingService для бизнес-логики

## Приоритет: 🟢 Низкий

## Описание
Класс `BookingService` в `bot/services/booking_service.py` создан, но не используется.
Вся логика бронирования находится в `create_booking_request()` в handlers.

## Текущее состояние
- `BookingService` содержит методы:
  - `calculate_booking_price()`
  - `validate_booking_dates()`
  - `check_availability()`
  - `get_platform_fee()`
- Эти методы НЕ используются в handlers

## Решение

### Рефакторинг create_booking_request()
```python
from services.booking_service import BookingService

async def create_booking_request(message: Message, state: FSMContext, user: dict):
    data = await state.get_data()
    apartment_id = data.get('booking_apartment_id')
    filters = data.get('filters', {})
    lang = user['language']

    # Использовать сервис
    service = BookingService()
    
    # Валидация дат
    is_valid, error = service.validate_booking_dates(
        filters['check_in'], 
        filters['check_out']
    )
    if not is_valid:
        await message.answer(error, reply_markup=get_main_menu_keyboard(lang))
        return

    # Проверка доступности
    if not service.check_availability(apartment_id, filters['check_in'], filters['check_out']):
        await message.answer(get_text('apartment_booked', lang), ...)
        return

    # Расчёт цены
    total_price, original_price, days, has_discount, discount_days = \
        service.calculate_booking_price(
            apartment_id, user['id'], 
            filters['check_in'], filters['check_out']
        )

    platform_fee = service.get_platform_fee(total_price)
    
    # Создание бронирования...
```

## Проверка
- [ ] Вся бизнес-логика бронирования в BookingService
- [ ] Handlers только вызывают сервис и обрабатывают UI
