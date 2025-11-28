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
| `admin/` | Admin panel (PHP 7.4+, Bootstrap 5) |
| `database/` | SQLite database and migrations |
| `uploads/apartments/` | Apartment photo storage |

## Bot Architecture

**Data flow:** `main.py` → `handlers/` → `services/` → `database.py`

### Key Files
- `main.py` — Entry point, FSM state definitions, core handlers
- `database.py` — All SQLite operations (single data access layer)
- `locales.py` — i18n strings (`MESSAGES` dict with `ru`/`kk` keys)
- `keyboards.py` — Inline and Reply keyboard builders
- `constants.py` — Application limits, rates, magic numbers

### Conventions
- Use `get_text(key, lang, **kwargs)` for all user-facing strings
- FSM states defined as `StatesGroup` classes in `main.py`
- Handlers receive `message`/`callback_query` and `state` from aiogram
- Services contain business logic, handlers handle user interaction only

## Admin Panel Architecture

- Each PHP file is a standalone page with `header.php`/`footer.php` includes
- `config.php` — Database connection, auth helpers, session management
- Bootstrap 5 via CDN for UI components

## Database Schema

| Table | Purpose |
|-------|---------|
| `users` | Users with roles: user, landlord, admin |
| `apartments` | Rental listings with photos, amenities |
| `bookings` | Booking records with status tracking |
| `reviews` | User reviews and ratings |
| `favorites` | User saved apartments |
| `promotions` | Promotional offers (N-th booking free) |
| `cities`, `districts` | Geographic hierarchy |

## Code Conventions

### Python (Bot)
- Async/await for all I/O operations
- Type hints encouraged
- Logging via `bot/logger.py`
- Rate limiting via `bot/rate_limiter.py`

### PHP (Admin)
- Include auth check at top of protected pages
- Use prepared statements for all SQL queries
- Escape output with `htmlspecialchars()`

### Shared
- Single SQLite database at `database/rental.db`
- Schema source of truth: `database/schema.sql`
