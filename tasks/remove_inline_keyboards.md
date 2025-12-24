# Задача: Убрать inline-кнопки после использования

## Цель
Убирать inline-кнопки с предыдущих сообщений чтобы пользователь не мог нажать на устаревшие кнопки.

## Уже сделано ✅
- `bot/handlers/search.py`:
  - `process_city_selection` — убирает кнопки при выборе города
  - `process_district_selection` — убирает кнопки при выборе района
  - `show_apartment` — удаляет все сообщения предыдущей карточки квартиры

## Выполнено ✅

### bot/handlers/booking.py
- [x] `start_booking` — убирает кнопки с карточки квартиры при начале бронирования
- [x] `cancel_booking_confirm` — убирает кнопки после подтверждения отмены
- [x] `confirm_cancel_booking` — уже использует edit_text (заменяет кнопки)
- [x] `keep_booking` — уже использует edit_text (заменяет кнопки)

### bot/handlers/calendar.py
- [x] `calendar_navigation` — оставлен edit (уже заменяет кнопки)
- [x] `select_date` — убирает кнопки календаря после выбора даты (check_out и non-booking flow)
- [x] `calendar_back` — убирает кнопки при возврате

### bot/handlers/favorites.py
- [x] `add_to_favorites` — уже использует edit_reply_markup (заменяет кнопки)
- [x] `remove_from_favorites` — уже использует edit_reply_markup (заменяет кнопки)
- [x] `confirm_unfavorite` — убирает кнопки после подтверждения
- [x] `keep_favorite` — убирает кнопки после "оставить"

### bot/handlers/reviews.py
- [x] `start_review` — убирает кнопки при начале отзыва
- [x] `show_reviews` — убирает кнопки при показе отзывов
- [x] `select_rating` — убирает кнопки после выбора рейтинга
- [x] `rate_cleanliness` — убирает кнопки
- [x] `rate_accuracy` — убирает кнопки
- [x] `rate_communication` — убирает кнопки
- [x] `rate_location` — убирает кнопки
- [x] `skip_detailed_ratings` — убирает кнопки
- [x] `skip_review_comment` — убирает кнопки
- [x] `reviews_pagination` — оставлен edit (уже заменяет кнопки)
- [x] `reviews_back` — убирает кнопки

### bot/handlers/registration.py
- [x] `process_language_selection` — убирает кнопки после выбора языка

### bot/handlers/common.py
- [x] Уже используют `edit_text` — кнопки заменяются автоматически

## Паттерн для реализации

```python
# В начале callback обработчика добавить:
try:
    await callback.message.edit_reply_markup(reply_markup=None)
except Exception:
    pass
```

## Статус
✅ Завершено
