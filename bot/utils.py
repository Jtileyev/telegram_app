"""
Utility functions for the bot
"""
import os
import re
from aiogram.types import Message, FSInputFile, InputMediaPhoto

import database as db
from locales import get_text
from constants import MAX_PHOTOS_PER_MESSAGE, PRICE_THOUSANDS_SEPARATOR


def pluralize_days(count: int, lang: str) -> str:
    """Return correct plural form for days in given language"""
    if lang == 'kk':
        return get_text('day_singular', lang)  # Kazakh has no plural forms
    
    # Russian plural rules
    if count % 10 == 1 and count % 100 != 11:
        return get_text('day_singular', lang)
    elif count % 10 in [2, 3, 4] and count % 100 not in [12, 13, 14]:
        return get_text('day_few', lang)
    else:
        return get_text('day_many', lang)


def validate_phone(phone: str) -> bool:
    """Validate phone number format

    Supported formats:
    - +7 (XXX) XXX XX XX
    - +7 XXX XXX XX XX
    - 7 XXX XXX XX XX
    - 8 XXX XXX XX XX
    """
    cleaned = re.sub(r'[\s\(\)\-]', '', phone)

    if cleaned.startswith('8'):
        cleaned = '7' + cleaned[1:]

    if not cleaned.startswith('+'):
        cleaned = '+' + cleaned

    return bool(re.match(r'^\+7\d{10}$', cleaned))


def format_price(price: float) -> str:
    """Format price with thousands separator"""
    return "{:,.0f}".format(price).replace(',', PRICE_THOUSANDS_SEPARATOR)


def format_apartment_card(apartment: dict, lang: str = 'ru', user_id: int = None) -> str:
    """Format apartment information as text"""
    title_key = 'title_ru' if lang == 'ru' else 'title_kk'
    desc_key = 'description_ru' if lang == 'ru' else 'description_kk'

    text = f"🏠 *{apartment[title_key]}*\n\n"

    if apartment.get('promotion_name'):
        promo_text = f"🎁 *{apartment['promotion_name']}*\n"
        free_days = apartment['promotion_free_days']
        promo_text += f"   {apartment['promotion_bookings_required']}-"
        promo_text += ("е заселение → " if lang == 'ru' else " орналасу → ")
        promo_text += f"{free_days} {pluralize_days(free_days, lang)} {get_text('free_days', lang)}\n"

        if user_id:
            progress = db.get_user_promotion_progress(user_id, apartment['id'])
            if progress:
                current = progress['completed_bookings']
                required = progress['bookings_required']
                progress_label = "Ваш прогресс" if lang == 'ru' else "Сіздің прогресіңіз"
                promo_text += f"   📊 {progress_label}: {current}/{required}\n"
                if current + 1 >= required:
                    bonus_text = "Следующее бронирование — с бонусом!" if lang == 'ru' else "Келесі броньдау — бонуспен!"
                    promo_text += f"   ✨ {bonus_text}\n"

        text += promo_text + "\n"

    text += get_text('price_per_day', lang, price=format_price(apartment['price_per_day'])) + "\n"
    text += get_text('address', lang, address=apartment['address']) + "\n\n"

    if apartment['reviews_count'] > 0:
        text += get_text('rating', lang, rating=apartment['rating'], count=apartment['reviews_count']) + "\n\n"
    else:
        text += get_text('no_reviews', lang) + "\n\n"

    if apartment.get(desc_key):
        text += f"{apartment[desc_key]}\n\n"

    if apartment.get('amenities'):
        text += get_text('amenities', lang) + "\n"
        for amenity in apartment['amenities']:
            text += f"• {amenity}\n"
        text += "\n"

    if apartment.get('gis_link'):
        text += f"🗺 [2GIS]({apartment['gis_link']})\n"

    return text


async def send_apartment_card(message: Message, apartment: dict, keyboard, lang: str, user_id: int = None):
    """Send apartment card with photos and keyboard"""
    from logger import setup_logger
    logger = setup_logger('utils')

    text = format_apartment_card(apartment, lang, user_id)
    photos = apartment.get('photos', [])

    # Filter only existing photo files
    valid_photos = [p for p in photos if os.path.exists(p)]
    
    if valid_photos:
        try:
            media_group = []
            for i, photo_path in enumerate(valid_photos[:MAX_PHOTOS_PER_MESSAGE]):
                try:
                    photo = FSInputFile(photo_path)
                    if i == 0:
                        media_group.append(InputMediaPhoto(media=photo, caption=text, parse_mode="Markdown"))
                    else:
                        media_group.append(InputMediaPhoto(media=photo))
                except Exception as e:
                    logger.warning(f"Failed to load photo {photo_path}: {e}")
                    continue

            if media_group:
                await message.answer_media_group(media=media_group)
            else:
                # All photos failed to load
                await message.answer(text, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Error sending photos: {e}")
            await message.answer(text, parse_mode="Markdown")
    else:
        await message.answer(text, parse_mode="Markdown")

    await message.answer(get_text('actions_prompt', lang), reply_markup=keyboard)
