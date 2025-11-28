"""
Utility functions for the bot
"""
import re
from aiogram.types import Message, FSInputFile, InputMediaPhoto

import database as db
from locales import get_text
from constants import MAX_PHOTOS_PER_MESSAGE, PRICE_THOUSANDS_SEPARATOR


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
        promo_text += f"   {apartment['promotion_bookings_required']}-е заселение → {apartment['promotion_free_days']} "
        promo_text += "день" if apartment['promotion_free_days'] == 1 else "дня" if apartment['promotion_free_days'] < 5 else "дней"
        promo_text += " бесплатно\n"

        if user_id:
            progress = db.get_user_promotion_progress(user_id, apartment['id'])
            if progress:
                current = progress['completed_bookings']
                required = progress['bookings_required']
                promo_text += f"   📊 Ваш прогресс: {current}/{required}\n"
                if current + 1 >= required:
                    promo_text += f"   ✨ Следующее бронирование — с бонусом!\n"

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

    if photos:
        try:
            media_group = []
            for i, photo_path in enumerate(photos[:MAX_PHOTOS_PER_MESSAGE]):
                photo = FSInputFile(photo_path)
                if i == 0:
                    media_group.append(InputMediaPhoto(media=photo, caption=text, parse_mode="Markdown"))
                else:
                    media_group.append(InputMediaPhoto(media=photo))

            await message.answer_media_group(media=media_group)
        except Exception as e:
            logger.error(f"Error sending photos: {e}")
            await message.answer(text, parse_mode="Markdown")
    else:
        await message.answer(text, parse_mode="Markdown")

    await message.answer("👇 Действия:", reply_markup=keyboard)
