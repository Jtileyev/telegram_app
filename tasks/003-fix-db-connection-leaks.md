# Задача 003: Исправить утечки соединений БД

## Приоритет: 🟡 Средний

## Описание
В некоторых функциях `database.py` соединение может не закрыться при возникновении исключения.

## Решение

### Вариант 1: Context Manager
Создать context manager для работы с БД:

```python
from contextlib import contextmanager

@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()

# Использование:
def get_user(telegram_id: int) -> Optional[Dict[str, Any]]:
    with get_db() as conn:
        cursor = conn.execute(
            "SELECT * FROM users WHERE telegram_id = ?",
            (telegram_id,)
        )
        user = cursor.fetchone()
        return dict(user) if user else None
```

### Вариант 2: try/finally
Добавить try/finally во все функции:

```python
def get_user(telegram_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    try:
        cursor = conn.execute(...)
        user = cursor.fetchone()
        return dict(user) if user else None
    finally:
        conn.close()
```

## Затронутые функции
- `get_user()`
- `get_user_language()`
- `has_role()`
- `get_user_roles()`
- `get_cities()`
- `get_districts()`
- И другие...

## Проверка
- [ ] Все функции БД используют context manager или try/finally
- [ ] Нет утечек соединений при длительной работе бота
