# TODO: Оставшиеся задачи

## Завершенные задачи ✅
- [x] Добавлены QA тесты (bot/tests.py)
- [x] Добавлена страница QA тестов в админке (admin/qa_tests.php)
- [x] Переделана форма авторизации через Email (admin/login.php)
- [x] Добавлена поддержка ролей (admin/config.php)
- [x] Обновлена схема БД - email обязателен, добавлено поле password

## Задачи в процессе 🔄

### 1. Исправить валидацию телефона
**Файлы:** `bot/main.py`
**Что сделать:**
```python
def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    # Очистить от пробелов и символов
    cleaned = re.sub(r'[\s\(\)\-]', '', phone)

    # Поддерживаемые форматы:
    # +7 (XXX) XXX XX XX
    # +7 XXX XXX XX XX
    # 7 XXX XXX XX XX
    # 8 XXX XXX XX XX

    # Заменить 8 на 7
    if cleaned.startswith('8'):
        cleaned = '7' + cleaned[1:]

    # Добавить + если нет
    if not cleaned.startswith('+'):
        cleaned = '+' + cleaned

    return bool(re.match(r'^\+7\d{10}$', cleaned))
```

### 2. Сделать Email обязательным
**Файлы:** `bot/main.py`, `admin/landlord_edit.php`, `admin/requests.php`
**Что сделать:**
- В боте: при подаче заявки арендодателя запрашивать email
- В админке: поле email обязательно при создании/редактировании арендодателя

### 3. Обновить header.php для ролей
**Файл:** `admin/header.php`
**Что сделать:**
```php
// Скрыть пункты меню для арендодателей
<?php if (isAdmin()): ?>
    <li class="nav-item">
        <a class="nav-link" href="users.php">
            <i class="bi bi-people me-2"></i>Пользователи
        </a>
    </li>
    <li class="nav-item">
        <a class="nav-link" href="cities.php">
            <i class="bi bi-geo-alt me-2"></i>Города и районы
        </a>
    </li>
    <li class="nav-item">
        <a class="nav-link" href="requests.php">
            <i class="bi bi-envelope me-2"></i>Заявки
        </a>
    </li>
    <li class="nav-item">
        <a class="nav-link" href="settings.php">
            <i class="bi bi-gear me-2"></i>Настройки
        </a>
    </li>
    <li class="nav-item">
        <a class="nav-link" href="qa_tests.php">
            <i class="bi bi-check2-square me-2"></i>QA Тесты
        </a>
    </li>
    <li class="nav-item">
        <a class="nav-link" href="sqlite_browser.php">
            <i class="bi bi-database me-2"></i>SQLite Browser
        </a>
    </li>
<?php endif; ?>
```

### 4. Фильтрация данных по landlord_id
**Файлы:** `admin/apartments.php`, `admin/bookings.php`, `admin/reviews.php`

**apartments.php:**
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

**bookings.php:**
```php
if (isLandlord()) {
    $query .= " WHERE b.landlord_id = ?";
    $stmt = $db->prepare($query);
    $stmt->execute([getLandlordId()]);
}
```

**reviews.php:**
```php
if (isLandlord()) {
    $query .= " WHERE a.landlord_id = ?";
    $stmt = $db->prepare($query);
    $stmt->execute([getLandlordId()]);
}
```

### 5. Убрать даты из поиска
**Файлы:** `bot/main.py`, `bot/keyboards.py`, `bot/database.py`

**Что сделать:**
- Убрать выбор дат check_in/check_out из процесса поиска
- Изменить SearchStates - убрать selecting_check_in и selecting_check_out
- Обновить get_apartments() - убрать фильтрацию по датам
- Даты выбираются только при бронировании

### 6. Календарь с блокировкой занятых дат
**Файлы:** `bot/keyboards.py`, `bot/main.py`

**get_calendar_keyboard():**
```python
def get_calendar_keyboard(apartment_id: int, year: int, month: int, lang: str,
                          min_date: datetime, selected_date: str = None,
                          calendar_type: str = 'check_in', check_in_date: str = None):
    # Получить забронированные даты для квартиры
    booked_dates = db.get_booked_dates(apartment_id)

    # При отрисовке дней:
    if date_str in booked_dates:
        row.append(InlineKeyboardButton(text="✖", callback_data="ignore"))
    elif ...:
        # Обычная логика
```

**database.py:**
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

### 7. Бронировать только после подтверждения
**Файл:** `bot/database.py`

**Обновить check_apartment_availability():**
```python
def check_apartment_availability(apartment_id: int, check_in: str, check_out: str):
    """Check if apartment is available (only confirmed bookings block dates)"""
    query = """
        SELECT COUNT(*) as count FROM bookings
        WHERE apartment_id = ?
        AND status = 'confirmed'  -- Только подтвержденные брони
        AND (...)
    """
```

### 8. Telegram уведомления арендодателям
**Файлы:** `admin/requests.php`, `bot/notifications.py`

**bot/notifications.py (создать новый файл):**
```python
import asyncio
from aiogram import Bot

async def send_notification(telegram_id: int, message: str):
    """Send notification to user via Telegram"""
    bot = Bot(token=BOT_TOKEN)
    try:
        await bot.send_message(telegram_id, message)
    finally:
        await bot.session.close()

def notify_landlord_approved(telegram_id: int, landlord_name: str):
    """Notify landlord that their request was approved"""
    message = f"""✅ Ваша заявка одобрена!

Здравствуйте, {landlord_name}!

Ваша заявка на подключение к платформе "Аставайся" была одобрена.

Вы можете войти в панель управления используя ваш email.

Добро пожаловать в нашу команду! 🎉"""

    asyncio.run(send_notification(telegram_id, message))
```

**admin/requests.php:**
```php
if (isset($_GET['approve'])) {
    // ... existing code ...

    // Send Telegram notification
    $notifyScript = __DIR__ . '/../bot/notify_landlord.py';
    $command = escapeshellcmd("python3 $notifyScript {$request['telegram_id']} approved");
    exec($command . " > /dev/null 2>&1 &");  // Run in background
}
```

## Как применить миграцию БД

```bash
cd /home/user/telegram_app
sqlite3 database/rental.db < database/migration_roles.sql
```

Или через админ-панель SQLite Browser выполнить:
```sql
ALTER TABLE landlords ADD COLUMN password TEXT;
```

## Тестирование

1. Запустить тесты: `cd bot && python3 tests.py`
2. Запустить через админку: admin/qa_tests.php

## Примечания
- Все локальное хранение - без облачных сервисов ✅
- База SQLite ✅
- Многоязычность RU/KK ✅
- Роли: admin и landlord ✅
