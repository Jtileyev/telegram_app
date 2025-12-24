# 🏠 Аставайся — Telegram Bot для посуточной аренды квартир

Telegram-бот для посуточной аренды квартир в Казахстане с PHP админ-панелью.

## 📁 Структура проекта

```
astavaisya/
├── bot/                          # Telegram бот (Python 3.8+ / aiogram 3.x)
│   ├── main.py                   # Точка входа, инициализация бота
│   ├── database.py               # Слой работы с SQLite
│   ├── keyboards.py              # Inline и Reply клавиатуры
│   ├── locales.py                # Локализация (RU/KK)
│   ├── config.py                 # Конфигурация из .env
│   ├── constants.py              # Константы приложения
│   ├── utils.py                  # Утилиты (валидация, форматирование)
│   ├── notifications.py          # Отправка уведомлений
│   ├── logger.py                 # Централизованное логирование
│   ├── rate_limiter.py           # Middleware для rate limiting
│   ├── handlers/                 # Обработчики команд и callback'ов
│   │   ├── registration.py       # Регистрация пользователей
│   │   ├── search.py             # Поиск квартир
│   │   ├── booking.py            # Бронирование
│   │   ├── favorites.py          # Избранное
│   │   ├── reviews.py            # Отзывы
│   │   └── landlords.py          # Раздел для арендодателей
│   └── services/                 # Бизнес-логика
│       ├── booking_service.py    # Сервис бронирования
│       └── notification_service.py # Сервис уведомлений
│
├── admin/                        # Админ-панель (PHP 7.4+ / Bootstrap 5)
│   ├── index.php                 # Дашборд со статистикой
│   ├── apartments.php            # Управление квартирами
│   ├── apartment_edit.php        # Редактирование квартиры
│   ├── bookings.php              # Управление бронированиями
│   ├── users.php                 # Пользователи
│   ├── landlords.php             # Арендодатели
│   ├── reviews.php               # Модерация отзывов
│   ├── cities.php                # Города и районы
│   ├── promotions.php            # Акции и скидки
│   ├── requests.php              # Заявки на подключение
│   ├── settings.php              # Настройки платформы
│   ├── translations.php          # Управление переводами
│   ├── login.php                 # Авторизация
│   ├── config.php                # Конфигурация
│   ├── db_admin.php              # Подключение к БД
│   └── phpliteadmin.php          # SQLite браузер
│
├── database/                     # База данных
│   ├── schema.sql                # SQL схема
│   ├── rental.db                 # SQLite файл БД
│   ├── init_database.py          # Инициализация БД
│   ├── reset_database.py         # Сброс БД
│   └── apply_promotions_migration.py  # Миграция акций
│
├── uploads/                      # Загруженные файлы
│   └── apartments/               # Фотографии квартир
│
├── logs/                         # Логи (создаётся автоматически)
│   ├── bot.log                   # Общие логи бота
│   ├── error.log                 # Ошибки
│   └── audit.log                 # Аудит действий
│
├── tasks/                        # Задачи по рефакторингу
│
├── scripts/                      # Служебные скрипты
│   ├── backup.sh                 # Резервное копирование
│   ├── restore.sh                # Восстановление из бэкапа
│   └── run_all_tests.sh          # Запуск всех тестов
│
├── .env.example                  # Пример переменных окружения
├── requirements.txt              # Python зависимости
├── start.sh                      # Скрипт запуска бота
└── stop.sh                       # Скрипт остановки бота
```

## 🔧 Архитектура

### Telegram Bot (Python)

```
┌─────────────────────────────────────────────────────────────┐
│                        main.py                               │
│  • Инициализация Bot и Dispatcher                           │
│  • Подключение middleware (rate_limiter)                    │
│  • Регистрация роутеров                                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      handlers/                               │
│  registration.py  │  search.py  │  booking.py               │
│  favorites.py     │  reviews.py │  landlords.py             │
│                                                              │
│  • Обработка команд и callback_query                        │
│  • FSM для многошаговых диалогов                            │
│  • Формирование ответов пользователю                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      services/                               │
│  booking_service.py  │  notification_service.py             │
│                                                              │
│  • Бизнес-логика                                            │
│  • Расчёт цен и скидок                                      │
│  • Валидация данных                                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      database.py                             │
│                                                              │
│  • CRUD операции                                            │
│  • Транзакции                                               │
│  • Защита от SQL injection (whitelist полей)                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   database/rental.db                         │
│                        (SQLite)                              │
└─────────────────────────────────────────────────────────────┘
```

### База данных

```
users ─────────────┬──────────────── apartments
  │                │                     │
  │                │                     │
  ▼                ▼                     ▼
bookings ◄──── favorites            apartment_photos
  │                                      │
  │                                      │
  ▼                                      │
reviews ◄────────────────────────────────┘
```

**Основные таблицы:**
- `users` — пользователи (с ролями: user, landlord, admin)
- `apartments` — квартиры
- `bookings` — бронирования
- `reviews` — отзывы
- `favorites` — избранное
- `promotions` — акции
- `cities`, `districts` — география

## 🚀 Установка

### 1. Клонирование и настройка окружения

```bash
git clone <repo>
cd astavaisya

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Установка зависимостей
pip install -r requirements.txt
```

### 2. Настройка переменных окружения

```bash
cp .env.example .env
```

Отредактируйте `.env`:
```env
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
DATABASE_PATH=database/rental.db
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### 3. Инициализация базы данных

```bash
python database/init_database.py
```

### 4. Запуск бота

**Development:**
```bash
# Через скрипт
./start.sh

# Или напрямую
cd bot && python main.py
```

**Production:**
```bash
# Управление через systemd сервис
sudo systemctl start astavaisya-bot    # Запуск
sudo systemctl stop astavaisya-bot     # Остановка
sudo systemctl restart astavaisya-bot  # Перезапуск
sudo systemctl status astavaisya-bot   # Статус
```

### 5. Запуск админ-панели

```bash
# Для разработки
cd admin && php -S localhost:8080

# Для production — настройте Apache/Nginx
```

**Вход в админку:**
- URL: http://localhost:8080
- Email и пароль настраиваются в `.env` файле (`ADMIN_EMAIL`, `ADMIN_PASSWORD`)
- При первом входе система предложит установить пароль

## 📱 Функции бота

### Для пользователей
- 🌐 Выбор языка (русский / қазақша)
- 🔍 Поиск квартир по городу и району
- 📅 Интерактивный календарь с занятыми датами
- 🏠 Карточки квартир с фото и описанием
- 📞 Бронирование с уведомлением арендодателя
- ⭐ Избранное
- 📋 История бронирований
- 📝 Отзывы и рейтинги (с модерацией)
- 🎁 Система акций (N-е бронирование бесплатно)

### Для администраторов
- 📊 Дашборд со статистикой
- 🏠 Управление квартирами и арендодателями
- ✅ Модерация отзывов (одобрение/отклонение)
- 🌐 Редактор переводов
- ⚙️ Настройки платформы

### Для арендодателей
- 📄 Просмотр условий сотрудничества
- 📝 Подача заявки на подключение
- 🔔 Уведомления о новых бронированиях

## 🛡️ Безопасность

- **CSRF защита** — все формы админ-панели защищены токенами
- **Rate limiting** для защиты от спама
- **Whitelist полей** для защиты от SQL injection
- **Хеширование паролей** через bcrypt
- Маскирование персональных данных в логах
- Валидация всех входных данных
- Транзакции для атомарности операций

## 📊 Логирование

Логи сохраняются в папке `logs/`:
- `bot.log` — все события бота
- `error.log` — только ошибки
- `audit.log` — аудит критических операций (регистрации, бронирования)

Ротация: 10 MB на файл, 5 бэкапов.

## 🧪 Тестирование

```bash
# Запуск тестов
source venv/bin/activate
pytest bot/tests.py -v

# Запуск с покрытием
pytest --cov=bot bot/tests.py
```

Тесты находятся в `bot/tests.py` и проверяют:
- Работу с базой данных
- Локализацию
- Валидацию данных
- Бизнес-логику бронирований

## 🔄 Резервное копирование

```bash
# Создать бэкап
./scripts/backup.sh

# Восстановить из бэкапа
./scripts/restore.sh backup_20240115_120000
```

## 🌍 Локализация

Поддерживаемые языки:
- 🇷🇺 Русский
- 🇰🇿 Қазақша

Все тексты в `bot/locales.py`. Переводы в админке: `admin/translations.php`.

## 📦 Зависимости

**Python:**
- aiogram 3.x — Telegram Bot API
- python-dotenv — переменные окружения
- bcrypt — хеширование паролей
- pytest, pytest-asyncio — тестирование

**PHP:**
- PHP 7.4+
- SQLite3 extension
- Bootstrap 5 (CDN)

## 📄 Лицензия

MIT License