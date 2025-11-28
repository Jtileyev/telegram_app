# Задача 009: Добавить систему миграций БД

## Приоритет: 🟢 Низкий

## Описание
Сейчас есть только `schema.sql` без версионирования. 
При изменении схемы нужно вручную обновлять БД.

## Решение

### Вариант 1: Простые SQL миграции
Создать папку `database/migrations/`:
```
database/
├── migrations/
│   ├── 001_initial.sql
│   ├── 002_add_promotions.sql
│   └── 003_add_user_states.sql
├── schema.sql
└── rental.db
```

### Создать скрипт миграций
```python
# database/migrate.py
import sqlite3
import os
from pathlib import Path

MIGRATIONS_DIR = Path(__file__).parent / 'migrations'
DB_PATH = Path(__file__).parent / 'rental.db'

def get_applied_migrations(conn):
    """Get list of applied migrations"""
    conn.execute('''
        CREATE TABLE IF NOT EXISTS migrations (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor = conn.execute('SELECT name FROM migrations ORDER BY id')
    return {row[0] for row in cursor.fetchall()}

def apply_migrations():
    """Apply pending migrations"""
    conn = sqlite3.connect(str(DB_PATH))
    applied = get_applied_migrations(conn)
    
    migration_files = sorted(MIGRATIONS_DIR.glob('*.sql'))
    
    for migration_file in migration_files:
        name = migration_file.name
        if name not in applied:
            print(f"Applying migration: {name}")
            with open(migration_file, 'r') as f:
                conn.executescript(f.read())
            conn.execute('INSERT INTO migrations (name) VALUES (?)', (name,))
            conn.commit()
            print(f"✓ Applied: {name}")
    
    conn.close()
    print("All migrations applied!")

if __name__ == '__main__':
    apply_migrations()
```

### Вариант 2: Использовать Alembic
Для более сложных проектов можно использовать Alembic с SQLAlchemy.

## Проверка
- [ ] Миграции применяются автоматически при запуске
- [ ] Повторное применение не вызывает ошибок
- [ ] История миграций сохраняется в БД
