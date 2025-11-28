---
inclusion: always
---

# Project Structure & Architecture

## Directory Layout

| Path | Purpose |
|------|---------|
| `bot/` | Telegram bot (Python 3.8+, aiogram 3.x) |
| `bot/handlers/` | User interaction handlers by feature |
| `bot/services/` | Business logic layer |
| `bot/middleware/` | Request middleware (error handling, rate limiting) |
| `admin/` | Admin panel (PHP 7.4+, Bootstrap 5) |
| `database/` | SQLite database and migrations |
| `uploads/apartments/` | Apartment photo storage |

## Bot Architecture

**Data flow:** `main.py` → `handlers/` → `services/` → `database.py`

### Key Files
- `main.py` — Entry point, router registration, middleware setup, background tasks
- `database.py` — All SQLite operations (single data access layer)
- `locales.py` — i18n strings (`MESSAGES` dict with `ru`/`kk` keys)
- `keyboards.py` — Inline and Reply keyboard builders
- `constants.py` — Application limits, rates, magic numbers
- `config.py` — Environment configuration and bot token management

### Handler Pattern
```python
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import database as db
from locales import get_text
from keyboards import get_*_keyboard

router = Router()

class MyStates(StatesGroup):
    state_name = State()

@router.callback_query(F.data.startswith("prefix_"))
async def handler(callback: CallbackQuery, state: FSMContext):
    telegram_id = callback.from_user.id
    user = db.get_user(telegram_id)
    lang = user['language']
    # Always validate data exists before use
    # Use get_text(key, lang, **kwargs) for user-facing strings
```

### Conventions
- Use `get_text(key, lang, **kwargs)` for ALL user-facing strings
- FSM states defined as `StatesGroup` classes in handler files
- Handlers receive `message`/`callback_query` and `state` from aiogram
- Services contain business logic, handlers handle user interaction only
- Always validate user input and entity existence before operations
- Use `db.get_user(telegram_id)` to get user, then access `user['language']`
- Callback data format: `action_entityid` (e.g., `book_123`, `fav_456`)

### Database Access
- Use context manager `with get_db() as conn:` for simple queries
- Use `get_connection()` directly only when needing multiple operations
- Always close connections explicitly when using `get_connection()`
- Use `BookingStatus` enum instead of magic strings for booking statuses
- Field whitelists (`ALLOWED_*_FIELDS`) prevent SQL injection in dynamic updates

## Admin Panel Architecture

### Structure
- Each PHP file is a standalone page with `header.php`/`footer.php` includes
- `config.php` — Database connection, auth helpers, session management
- Bootstrap 5 via CDN for UI components

### Security Pattern
```php
<?php
require_once 'config.php';
requireLogin();  // or requireAdmin() for admin-only pages

// Use prepared statements
$stmt = $db->prepare("SELECT * FROM table WHERE id = ?");
$stmt->execute([$id]);

// Escape output
echo sanitize($userInput);
```

### Helper Functions
- `isLoggedIn()`, `isAdmin()`, `isLandlord()` — Auth checks
- `requireLogin()`, `requireAdmin()` — Redirect guards
- `getDB()` — PDO connection singleton
- `sanitize($input)` — XSS protection via `htmlspecialchars()`
- `setFlash($type, $message)`, `getFlash()` — Flash messages

## Database Schema

| Table | Purpose |
|-------|---------|
| `users` | Users with JSON `roles` field: user, landlord, admin |
| `apartments` | Rental listings with JSON `amenities`, `promotion_id` FK |
| `bookings` | Booking records with status: pending, confirmed, completed, rejected, cancelled |
| `reviews` | User reviews with detailed ratings (cleanliness, accuracy, etc.) |
| `favorites` | User saved apartments (user_id, apartment_id) |
| `promotions` | N-th booking free offers |
| `user_promotion_progress` | Tracks user progress toward promotions |
| `cities`, `districts` | Geographic hierarchy (city_id FK in districts) |
| `messages` | Booking-related chat messages |
| `settings` | Key-value application settings |

## Code Conventions

### Python (Bot)
- Async/await for all I/O operations
- Type hints on function signatures
- Logging via `bot/logger.py` — use `setup_logger(name)` per module
- Rate limiting via `bot/rate_limiter.py` middleware
- Constants in `constants.py` — no magic numbers in handlers
- Price formatting via `utils.format_price()` with `PRICE_CURRENCY` constant

### PHP (Admin)
- Include auth check at top of protected pages
- Use prepared statements for ALL SQL queries
- Escape output with `sanitize()` or `htmlspecialchars()`
- Use `formatPrice()` and `formatDate()` helpers for display

### Localization
- Two languages: Russian (`ru`) and Kazakh (`kk`)
- All strings in `bot/locales.py` MESSAGES dict
- Access via `get_text(key, lang, **kwargs)` — supports string interpolation
- Add new keys to BOTH language sections

### Shared
- Single SQLite database at `database/rental.db`
- Schema source of truth: `database/schema.sql`
- User roles stored as JSON array in `users.roles` column
