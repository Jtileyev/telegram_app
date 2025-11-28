# Задача 001: Исправить синтаксические ошибки в regex-паттернах

## Приоритет: 🔴 Критический

## Описание
В нескольких файлах обнаружены незавершённые regex-паттерны, которые приводят к синтаксическим ошибкам.

## Затронутые файлы
- `bot/utils.py` — функция `validate_phone()`
- `bot/main.py` — функция `validate_phone()` (дубликат)
- `bot/handlers/landlords.py` — функция `process_landlord_email()`, переменная `email_pattern`

## Что исправить

### bot/utils.py
```python
# Было (обрезано):
return bool(re.match(r'^\+7\d{10}

# Должно быть:
return bool(re.match(r'^\+7\d{10}$', cleaned))
```

### bot/handlers/landlords.py
```python
# Было (обрезано):
email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}

# Должно быть:
email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
```

## Проверка
- [ ] Бот запускается без ошибок
- [ ] Валидация телефона работает корректно
- [ ] Валидация email работает корректно
