# Tech Stack

## Telegram Bot (Python)
- **Python 3.8+**
- **aiogram 3.x** — Telegram Bot API framework
- **python-dotenv** — Environment configuration
- **SQLite** — Database (shared with admin panel)
- **bcrypt** — Password hashing

## Admin Panel (PHP)
- **PHP 7.4+**
- **Bootstrap 5** (CDN) — UI framework
- **SQLite3** extension
- **phpLiteAdmin** — Database browser

## Database
- **SQLite** — Single file database at `database/rental.db`
- Schema defined in `database/schema.sql`

## Common Commands

### Bot Setup & Run
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_database.py

# Start bot
./start.sh
# or: cd bot && python main.py

# Stop bot
./stop.sh
```

### Admin Panel
```bash
# Development server
cd admin && php -S localhost:8080

# Default login: admin / admin123
```

### Database
```bash
# Reset database
python reset_database.py

# Backup
./backup.sh

# Restore
./restore.sh backups/backup_YYYY-MM-DD.tar.gz
```

## Environment Variables
Copy `.env.example` to `.env` and configure:
- `BOT_TOKEN` — Telegram bot token (required)
- `DATABASE_PATH` — Path to SQLite database
- `ENVIRONMENT` — development/production
- `LOG_LEVEL` — INFO/DEBUG/ERROR
