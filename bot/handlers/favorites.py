"""
Favorites handlers - favorite apartments management
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import database as db
from keyboards import get_apartment_card_keyboard
from locales import get_text
from utils import send_apartment_card

router = Router()


@router.message(F.text.in_([
    "❤️ Избранное", "❤️ Таңдаулылар"
]))
async def handle_favorites(message: Message, state: FSMContext):
    """Handle favorites button"""
    telegram_id = message.from_user.id
    user = db.get_user(telegram_id)
    lang = user['language']

    favorites = db.get_user_favorites(user['id'])

    if not favorites:
        await message.answer(get_text('favorites_empty', lang))
        return

    await message.answer(get_text('favorites_title', lang))
    await state.update_data(favorites=favorites, fav_index=0)

    await show_favorite_apartment(message, state, 0)


async def show_favorite_apartment(message: Message, state: FSMContext, index: int):
    """Show favorite apartment by index"""
    data = await state.get_data()
    favorites = data.get('favorites', [])

    if not favorites or index < 0 or index >= len(favorites):
        return

    apartment = favorites[index]
    telegram_id = message.from_user.id
    user = db.get_user(telegram_id)
    lang = user['language']

    has_prev = index > 0
    has_next = index < len(favorites) - 1

    keyboard = get_apartment_card_keyboard(
        apartment['id'],
        is_favorite=True,
        lang=lang,
        has_prev=has_prev,
        has_next=has_next
    )

    await send_apartment_card(message, apartment, keyboard, lang)
    await state.update_data(fav_index=index)


@router.callback_query(F.data.startswith("fav_"))
async def add_to_favorites(callback: CallbackQuery, state: FSMContext):
    """Add apartment to favorites"""
    apartment_id = int(callback.data.split("_")[1])
    telegram_id = callback.from_user.id
    user = db.get_user(telegram_id)
    lang = user['language']

    # Validate apartment exists
    apartment = db.get_apartment_by_id(apartment_id)
    if not apartment:
        await callback.answer(get_text('apartment_not_found', lang), show_alert=True)
        return

    db.add_to_favorites(user['id'], apartment_id)
    await callback.answer(get_text('added_to_favorites', lang))

    data = await state.get_data()
    apartments = data.get('apartments', [])
    apt_index = data.get('apt_index', 0)

    if apartments:
        has_prev = apt_index > 0
        has_next = apt_index < len(apartments) - 1

        keyboard = get_apartment_card_keyboard(
            apartment_id, is_favorite=True, lang=lang,
            has_prev=has_prev, has_next=has_next
        )
        await callback.message.edit_reply_markup(reply_markup=keyboard)


@router.callback_query(F.data.startswith("unfav_"))
async def remove_from_favorites(callback: CallbackQuery, state: FSMContext):
    """Remove apartment from favorites"""
    apartment_id = int(callback.data.split("_")[1])
    telegram_id = callback.from_user.id
    user = db.get_user(telegram_id)
    lang = user['language']

    # Validate apartment exists
    apartment = db.get_apartment_by_id(apartment_id)
    if not apartment:
        await callback.answer(get_text('apartment_not_found', lang), show_alert=True)
        return

    db.remove_from_favorites(user['id'], apartment_id)
    await callback.answer(get_text('removed_from_favorites', lang))

    data = await state.get_data()
    apartments = data.get('apartments', [])
    apt_index = data.get('apt_index', 0)

    if apartments:
        has_prev = apt_index > 0
        has_next = apt_index < len(apartments) - 1

        keyboard = get_apartment_card_keyboard(
            apartment_id, is_favorite=False, lang=lang,
            has_prev=has_prev, has_next=has_next
        )
        await callback.message.edit_reply_markup(reply_markup=keyboard)


@router.callback_query(F.data.startswith("confirm_unfav_"))
async def confirm_unfavorite(callback: CallbackQuery):
    """Confirm remove from favorites"""
    apartment_id = int(callback.data.split("_")[2])
    telegram_id = callback.from_user.id
    user = db.get_user(telegram_id)
    lang = user['language']

    # Validate apartment exists
    apartment = db.get_apartment_by_id(apartment_id)
    if not apartment:
        await callback.answer(get_text('apartment_not_found', lang), show_alert=True)
        return

    db.remove_from_favorites(user['id'], apartment_id)
    await callback.message.edit_text(get_text('removed_from_favorites', lang))
    await callback.answer()


@router.callback_query(F.data.startswith("keep_fav_"))
async def keep_favorite(callback: CallbackQuery):
    """Keep in favorites"""
    telegram_id = callback.from_user.id
    lang = db.get_user_language(telegram_id)

    await callback.message.delete()
    await callback.answer(get_text('kept_in_favorites', lang))
