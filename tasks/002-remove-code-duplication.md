# Задача 002: Устранить дублирование кода в main.py

## Приоритет: 🔴 Критический

## Описание
Файл `bot/main.py` содержит ~1400 строк кода с дублированием логики из папки `handlers/`. 
Обработчики определены и в `main.py`, и в отдельных файлах, но роутеры из handlers/ НЕ подключены к диспетчеру.

## Проблема
- Код дублируется в двух местах
- Изменения нужно вносить в нескольких файлах
- Handlers из `bot/handlers/` не используются

## Решение

### Шаг 1: Очистить main.py
Оставить только:
- Импорты
- Инициализацию бота и диспетчера
- Функцию `main()`
- Подключение роутеров

### Шаг 2: Подключить роутеры из handlers/
```python
from handlers.registration import router as registration_router
from handlers.search import router as search_router
from handlers.booking import router as booking_router
from handlers.favorites import router as favorites_router
from handlers.reviews import router as reviews_router
from handlers.landlords import router as landlords_router

# В функции main():
dp.include_router(registration_router)
dp.include_router(search_router)
dp.include_router(booking_router)
dp.include_router(favorites_router)
dp.include_router(reviews_router)
dp.include_router(landlords_router)
```

### Шаг 3: Перенести недостающие обработчики
Некоторые обработчики есть только в main.py:
- `handle_history` → перенести в новый `handlers/history.py`
- `handle_clear_chat` → перенести в `handlers/common.py`
- `handle_change_language` → перенести в `handlers/common.py`
- `calendar_navigation`, `select_date` → перенести в `handlers/calendar.py`
- `ignore_callback`, `search_back`, `filters_back` → перенести в `handlers/common.py`

## Проверка
- [ ] main.py содержит < 100 строк
- [ ] Все функции бота работают как раньше
- [ ] Нет дублирования кода
