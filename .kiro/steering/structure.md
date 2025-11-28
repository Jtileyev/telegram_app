# Project Structure

```
astavaisya/
├── bot/                    # Telegram bot (Python)
│   ├── main.py             # Entry point, bot initialization, core handlers
│   ├── config.py           # Configuration from .env
│   ├── constants.py        # Application constants (limits, rates, etc.)
│   ├── database.py         # SQLite operations layer
│   ├── keyboards.py        # Inline and Reply keyboards
│   ├── locales.py          # i18n strings (RU/KK)
│   ├── logger.py           # Centralized logging
│   ├── rate_limiter.py     # Rate limiting middleware
│   ├── notifications.py    # Notification sending
│   ├── utils.py            # Validation, formatting utilities
│   ├── handlers/           # Command and callback handlers
│   │   ├── registration.py
│   │   ├── search.py
│   │   ├── booking.py
│   │   ├── favorites.py
│   │   ├── reviews.py
│   │   └── landlords.py
│   └── services/           # Business logic layer
│       ├── booking_service.py
│       └── notification_service.py
│
├── admin/                  # Admin panel (PHP)
│   ├── config.php          # Configuration, auth helpers
│   ├── header.php          # Common header
│   ├── footer.php          # Common footer
│   ├── index.php           # Dashboard
│   ├── apartments.php      # Apartment management
│   ├── bookings.php        # Booking management
│   ├── users.php           # User management
│   ├── landlords.php       # Landlord management
│   ├── reviews.php         # Review moderation
│   ├── promotions.php      # Promotions management
│   ├── settings.php        # Platform settings
│   └── phpliteadmin.php    # SQLite browser
│
├── database/
│   ├── schema.sql          # Database schema
│   └── rental.db           # SQLite database file
│
├── uploads/
│   └── apartments/         # Apartment photos
│
├── tasks/                  # Refactoring tasks documentation
│
├── .env.example            # Environment template
├── requirements.txt        # Python dependencies
├── init_database.py        # Database initialization
├── start.sh / stop.sh      # Bot lifecycle scripts
└── backup.sh / restore.sh  # Database backup scripts
```

## Architecture Patterns

### Bot Layer Structure
```
main.py (entry) → handlers/ (user interaction) → services/ (business logic) → database.py (data access)
```

### Key Tables
- `users` — Users with roles (user, landlord, admin)
- `apartments` — Rental listings
- `bookings` — Booking records
- `reviews` — User reviews
- `favorites` — Saved apartments
- `promotions` — Promotional offers
- `cities`, `districts` — Geography

### Localization
All user-facing strings in `bot/locales.py` as `MESSAGES` dict with `ru` and `kk` keys.
Use `get_text(key, lang, **kwargs)` for translations.

### FSM States
Defined in `main.py` as `StatesGroup` classes:
- `RegistrationStates`
- `SearchStates`
- `BookingStates`
- `LandlordStates`
- `ReviewStates`
