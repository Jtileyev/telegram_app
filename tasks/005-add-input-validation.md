# Задача 005: Добавить валидацию входных данных

## Приоритет: 🟡 Средний

## Описание
В callback-обработчиках отсутствует валидация ID из callback_data.

## Проблемы

### 1. Отсутствует проверка существования apartment_id
```python
@router.callback_query(F.data.startswith("book_"))
async def start_booking(callback: CallbackQuery, state: FSMContext):
    apartment_id = int(callback.data.split("_")[1])  # Может быть несуществующий ID
    # ...
    apartment = db.get_apartment_by_id(apartment_id)
    # apartment может быть None!
```

### 2. Отсутствует проверка booking_id
```python
@router.callback_query(F.data.startswith("cancel_booking_"))
async def cancel_booking_confirm(callback: CallbackQuery):
    booking_id = int(callback.data.split("_")[2])
    # Нет проверки, что бронирование существует и принадлежит пользователю
```

## Решение

### Создать декоратор для валидации
```python
def validate_apartment(func):
    async def wrapper(callback: CallbackQuery, *args, **kwargs):
        apartment_id = int(callback.data.split("_")[1])
        apartment = db.get_apartment_by_id(apartment_id)
        if not apartment:
            lang = db.get_user_language(callback.from_user.id)
            await callback.answer(get_text('apartment_not_found', lang), show_alert=True)
            return
        return await func(callback, *args, apartment=apartment, **kwargs)
    return wrapper
```

### Добавить проверки в обработчики
```python
@router.callback_query(F.data.startswith("book_"))
async def start_booking(callback: CallbackQuery, state: FSMContext):
    apartment_id = int(callback.data.split("_")[1])
    apartment = db.get_apartment_by_id(apartment_id)
    
    if not apartment:
        lang = db.get_user_language(callback.from_user.id)
        await callback.answer(get_text('apartment_not_found', lang), show_alert=True)
        return
    
    if not apartment['is_active']:
        lang = db.get_user_language(callback.from_user.id)
        await callback.answer(get_text('apartment_inactive', lang), show_alert=True)
        return
    # ...
```

## Проверка
- [ ] Все callback-обработчики проверяют существование сущностей
- [ ] Пользователь получает понятное сообщение при ошибке
