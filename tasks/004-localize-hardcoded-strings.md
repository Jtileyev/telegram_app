# Задача 004: Локализовать hardcoded строки

## Приоритет: 🟡 Средний

## Описание
В коде есть русские строки, которые не локализованы для казахского языка.

## Найденные строки

### bot/utils.py и bot/main.py
```python
# Строка:
await message.answer("👇 Действия:", reply_markup=keyboard)

# Добавить в locales.py:
'actions_prompt': '👇 Действия:',  # ru
'actions_prompt': '👇 Әрекеттер:',  # kk
```

### bot/main.py и bot/handlers/booking.py
```python
# Склонение дней:
"день" if discount_days == 1 else "дня" if discount_days < 5 else "дней"

# Создать функцию pluralize() в utils.py:
def pluralize_days(count: int, lang: str) -> str:
    if lang == 'kk':
        return 'күн'  # В казахском нет склонения
    # Русское склонение
    if count % 10 == 1 and count % 100 != 11:
        return 'день'
    elif count % 10 in [2, 3, 4] and count % 100 not in [12, 13, 14]:
        return 'дня'
    else:
        return 'дней'
```

### bot/main.py
```python
# Строка:
await message.answer("🏠", reply_markup=get_main_menu_keyboard(lang))

# Это OK, эмодзи универсальны
```

## Проверка
- [ ] Все текстовые строки вынесены в locales.py
- [ ] Бот корректно отображает тексты на обоих языках
