# Задача 008: Улучшить обработку ошибок при отправке фото

## Приоритет: 🟡 Средний

## Описание
При отправке фото квартиры, если файл не существует или повреждён, бот может упасть.

## Текущий код
```python
async def send_apartment_card(message: Message, apartment: dict, keyboard, lang: str, user_id: int = None):
    photos = apartment.get('photos', [])
    if photos:
        try:
            media_group = []
            for i, photo_path in enumerate(photos[:MAX_PHOTOS_PER_MESSAGE]):
                photo = FSInputFile(photo_path)  # Может упасть если файла нет
                # ...
        except Exception as e:
            logger.error(f"Error sending photos: {e}")
            await message.answer(text, parse_mode="Markdown")
```

## Решение

### Проверять существование файлов
```python
import os
from pathlib import Path

async def send_apartment_card(message: Message, apartment: dict, keyboard, lang: str, user_id: int = None):
    text = format_apartment_card(apartment, lang, user_id)
    photos = apartment.get('photos', [])
    
    # Фильтруем только существующие файлы
    valid_photos = [p for p in photos if os.path.exists(p)]
    
    if valid_photos:
        try:
            media_group = []
            for i, photo_path in enumerate(valid_photos[:MAX_PHOTOS_PER_MESSAGE]):
                try:
                    photo = FSInputFile(photo_path)
                    if i == 0:
                        media_group.append(InputMediaPhoto(
                            media=photo, 
                            caption=text, 
                            parse_mode="Markdown"
                        ))
                    else:
                        media_group.append(InputMediaPhoto(media=photo))
                except Exception as e:
                    logger.warning(f"Failed to load photo {photo_path}: {e}")
                    continue
            
            if media_group:
                await message.answer_media_group(media=media_group)
            else:
                # Все фото не загрузились
                await message.answer(text, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Error sending photos: {e}")
            await message.answer(text, parse_mode="Markdown")
    else:
        await message.answer(text, parse_mode="Markdown")

    await message.answer(get_text('actions_prompt', lang), reply_markup=keyboard)
```

## Проверка
- [ ] Бот не падает при отсутствии фото
- [ ] Логируются предупреждения о недоступных файлах
- [ ] Карточка квартиры отображается даже без фото
