# Задача 004: Настройка .env файла

## Приоритет: 🔴 Высокий

## Описание
Проект не запустится без правильно настроенного `.env` файла. Нужно создать `.env` из шаблона и настроить.

## Шаги выполнения

### 1. Скопировать шаблон
```bash
cp .env.example .env
```

### 2. Получить токен бота
1. Открыть Telegram
2. Найти @BotFather
3. Создать нового бота: `/newbot`
4. Скопировать токен

### 3. Заполнить .env файл
```env
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz  # ваш токен
DATABASE_PATH=database/rental.db
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### 4. Проверить запуск
```bash
source venv/bin/activate
cd bot && python main.py
```

## Важно!
- `.env` файл НЕ должен попадать в git (он уже в `.gitignore`)
- Не делитесь токеном бота публично
- Для production использовать `ENVIRONMENT=production`

## Критерии завершения
- [ ] Создан файл `.env`
- [ ] Заполнен BOT_TOKEN
- [ ] Бот успешно запускается

## Связанные файлы
- `.env.example` - шаблон
- `.env` (создать) - рабочий файл
- `bot/config.py` - чтение конфига
