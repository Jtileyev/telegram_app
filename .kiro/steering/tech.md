---
inclusion: always
---

# Tech Stack

## Core Technologies

| Component | Stack |
|-----------|-------|
| Bot | Python 3.8+, aiogram 3.x, python-dotenv, bcrypt |
| Admin | PHP 7.4+, Bootstrap 5 (CDN), SQLite3 extension |
| Database | SQLite (`database/rental.db`), schema in `database/schema.sql` |
| DB Browser | phpLiteAdmin |

## Environment Setup

Required `.env` variables (copy from `.env.example`):
- `BOT_TOKEN` — Telegram bot token (required)
- `DATABASE_PATH` — SQLite database path
- `ENVIRONMENT` — `development` or `production`
- `LOG_LEVEL` — `INFO`, `DEBUG`, or `ERROR`

## Quick Reference Commands

| Task | Command |
|------|---------|
| Activate venv | `source venv/bin/activate` |
| Install deps | `pip install -r requirements.txt` |
| Init database | `python database/init_database.py` |
| Start bot | `./start.sh` or `cd bot && python main.py` |
| Stop bot | `./stop.sh` |
| Admin server | `cd admin && php -S localhost:8080` |
| Reset DB | `python database/reset_database.py` |
| Backup DB | `./scripts/backup.sh` |
| Restore DB | `./scripts/restore.sh backup_YYYYMMDD_HHMMSS` |

## Development Guidelines

- Always activate virtual environment before running Python code
- Admin panel default credentials: `admin` / `admin123`
- Database is shared between bot and admin — changes affect both
- Run `init_database.py` after schema changes
- Use `reset_database.py` only in development (destroys all data)
