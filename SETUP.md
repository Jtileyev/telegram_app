# Инструкция по настройке

## Установка зависимостей

### Для Python (бот и скрипты)

```bash
# Установка всех зависимостей из requirements.txt
pip install -r requirements.txt

# Или если используете venv (рекомендуется)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

### Минимальная установка (только bcrypt)

```bash
# Если нужен только bcrypt для хеширования паролей
pip install bcrypt
```

## Инициализация базы данных

### 1. Пересоздание базы данных (если нужно)

```bash
python3 reset_database.py
```

### 2. Заполнение данными

```bash
python3 init_database.py
```

## Учетные данные по умолчанию

**С bcrypt (рекомендуется):**
- Email: `atks0513@gmail.com`
- Password: *генерируется автоматически при запуске init_database.py*

**Без bcrypt (fallback):**
- Email: `atks0513@gmail.com`
- Password: `admin`
- ⚠️ Измените пароль сразу после первого входа!

## Смена пароля

Вы можете сменить пароль двумя способами:

1. **Через админ панель:**
   - Войдите в систему
   - Перейдите в настройки профиля
   - Измените пароль

2. **Через базу данных:**
   - Используйте phpLiteAdmin в админке
   - Или создайте новый хеш с помощью скрипта

## Структура проекта

```
telegram_app/
├── admin/              # Админ панель (PHP)
├── bot/                # Telegram бот (Python)
├── database/           # База данных SQLite
│   ├── rental.db      # Файл БД
│   └── schema.sql     # Схема БД
├── uploads/            # Загруженные файлы
├── init_database.py   # Скрипт инициализации
└── reset_database.py  # Скрипт пересоздания БД
```

## Решение проблем

### Ошибка: "bcrypt not available"

```bash
pip install bcrypt
```

### Ошибка: "no such column: email"

Ваша БД использует старую схему. Пересоздайте её:

```bash
python3 reset_database.py
python3 init_database.py
```

### Пароль не подходит

Если bcrypt не установлен, используется дефолтный пароль: `admin`

Установите bcrypt и пересоздайте админа:

```bash
pip install bcrypt
python3 init_database.py
```
