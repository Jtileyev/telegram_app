# Оставшиеся задачи для доработки

## ✅ Уже выполнено:
1. ✅ QA тесты добавлены
2. ✅ Валидация телефона исправлена (поддержка +7/7/8)
3. ✅ Email обязателен для арендодателей (в боте и БД)
4. ✅ Форма авторизации через email готова
5. ✅ Роли admin/landlord реализованы
6. ✅ Меню админки фильтруется по ролям

## 🔄 Требуется доработка:

### 1. Фильтрация данных в админке для арендодателей

**Файлы для обновления:**
- `admin/apartments.php`
- `admin/bookings.php`
- `admin/reviews.php`
- `admin/requests.php` (добавить email в создание landlord)

**Пример для apartments.php:**
```php
$query = "SELECT ... FROM apartments a WHERE 1=1";

if (isLandlord()) {
    $query .= " AND a.landlord_id = ?";
    $stmt = $db->prepare($query);
    $stmt->execute([getLandlordId()]);
} else {
    $stmt = $db->query($query);
}
```

**Для bookings.php:**
```php
if (isLandlord()) {
    $query .= " WHERE b.landlord_id = ?";
}
```

**Для reviews.php:**
```php
if (isLandlord()) {
    $query .= " WHERE a.landlord_id = ?";
}
```

**Для requests.php** (добавить email при approve):
```php
// В обработчике approve
$stmt = $db->prepare("INSERT INTO landlords (telegram_id, full_name, phone, email) VALUES (?, ?, ?, ?)");
$stmt->execute([$request['telegram_id'], $request['full_name'], $request['phone'], $request['email']]);
```

### 2. Убрать даты из поиска

**bot/main.py:**
- Удалить `selecting_check_in` и `selecting_check_out` из `SearchStates`
- Удалить обработчики выбора дат в поиске
- Даты будут выбираться только при бронировании

**bot/database.py:**
- В `get_apartments()` убрать параметры `check_in` и `check_out`

### 3. Календарь с блокировкой занятых дат

**bot/database.py** - добавить функцию:
```python
def get_booked_dates(apartment_id: int):
    """Get all booked dates for apartment (only confirmed bookings)"""
    conn = get_connection()
    cursor = conn.execute("""
        SELECT check_in_date, check_out_date
        FROM bookings
        WHERE apartment_id = ? AND status = 'confirmed'
    """, (apartment_id,))

    booked_dates = set()
    for row in cursor.fetchall():
        check_in = datetime.strptime(row['check_in_date'], "%Y-%m-%d").date()
        check_out = datetime.strptime(row['check_out_date'], "%Y-%m-%d").date()

        current = check_in
        while current < check_out:
            booked_dates.add(current.isoformat())
            current += timedelta(days=1)

    conn.close()
    return list(booked_dates)
```

**bot/keyboards.py** - обновить `get_calendar_keyboard()`:
```python
# Получить забронированные даты
booked_dates = db.get_booked_dates(apartment_id) if apartment_id else []

# При отрисовке дней:
if date_str in booked_dates:
    row.append(InlineKeyboardButton(text="✖", callback_data="ignore"))
```

### 4. Бронировать только после подтверждения

**bot/database.py** - обновить `check_apartment_availability()`:
```python
AND status = 'confirmed'  # Только подтвержденные брони
```

### 5. Telegram уведомления

**bot/notifications.py** (создать новый файл):
```python
import asyncio
from aiogram import Bot

async def send_notification(telegram_id: int, message: str, bot_token: str):
    """Send notification to user via Telegram"""
    bot = Bot(token=bot_token)
    try:
        await bot.send_message(telegram_id, message)
    finally:
        await bot.session.close()

def notify_landlord_approved(telegram_id: int, landlord_name: str, bot_token: str):
    """Notify landlord that their request was approved"""
    message = f"""✅ Ваша заявка одобрена!

Здравствуйте, {landlord_name}!

Ваша заявка на подключение к платформе "Аставайся" была одобрена.

Вы можете войти в панель управления используя ваш email.

Добро пожаловать в нашу команду! 🎉"""

    asyncio.run(send_notification(telegram_id, message, bot_token))
```

**bot/notify_landlord.py** (CLI скрипт):
```python
#!/usr/bin/env python3
import sys
from notifications import notify_landlord_approved
from config import BOT_TOKEN

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: notify_landlord.py <telegram_id> <name>")
        sys.exit(1)

    telegram_id = int(sys.argv[1])
    name = sys.argv[2]

    notify_landlord_approved(telegram_id, name, BOT_TOKEN)
```

**admin/requests.php** - вызывать уведомление при approve:
```php
// After creating landlord
$notifyScript = __DIR__ . '/../bot/notify_landlord.py';
$command = escapeshellcmd("python3 $notifyScript {$request['telegram_id']} '{$request['full_name']}'");
exec($command . " > /dev/null 2>&1 &");  // Run in background
```

## Миграция БД

```bash
cd /home/user/telegram_app
sqlite3 database/rental.db < database/migration_roles.sql
```

## Тестирование

1. Запустить тесты: `cd bot && python3 tests.py`
2. Проверить через админку: http://localhost:8080/qa_tests.php

## Порядок выполнения:

1. Фильтрация данных (4 файла)
2. Убрать даты из поиска
3. Календарь с блокировкой
4. Бронировать только confirmed
5. Telegram уведомления
6. Коммит и пуш

---
**Примечание:** Большая часть уже готова. Осталось доделать фильтрацию данных и переработку поиска.
