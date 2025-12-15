"""
Common handlers - main menu, history, language, calendar navigation
"""
from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import database as db
from keyboards import (
    get_main_menu_keyboard, get_language_keyboard, get_cities_keyboard,
    get_districts_keyboard, get_calendar_keyboard
)
from locales import get_text
from utils import format_price
from constants import BOOKINGS_HISTORY_LIMIT

router = Router()


# History handler
@router.message(F.text.in_([
    "📋 История аренды", "📋 Жалдау тарихы"
]))
async def handle_history(message: Message, state: FSMContext):
    """Handle history button"""
    from keyboards import get_booking_history_keyboard

    telegram_id = message.from_user.id
    user = db.get_user(telegram_id)
    lang = user['language']

    bookings = db.get_user_bookings(user['id'])

    if not bookings:
        await message.answer(get_text('history_empty', lang))
        return

    await message.answer(get_text('history_title', lang))

    for booking in bookings[:BOOKINGS_HISTORY_LIMIT]:
        status_key = f"status_{booking['status']}"
        title = booking['title_ru'] if lang == 'ru' else booking['title_kk']

        text = f"🏠 *{title}*\n"
        text += f"📍 {booking['address']}\n"
        text += f"📅 {booking['check_in_date']} - {booking['check_out_date']}\n"
        text += f"💰 {format_price(booking['total_price'])} ₸\n"
        text += f"{get_text(status_key, lang)}"

        # Check if user can leave review for completed bookings
        can_review = booking['status'] == 'completed' and db.can_leave_review(user['id'], booking['id'])

        await message.answer(
            text,
            parse_mode="Markdown",
            reply_markup=get_booking_history_keyboard(booking['id'], can_review, lang) if can_review else None
        )


# Language change handler
@router.message(F.text.in_([
    "🌐 Сменить язык", "🌐 Тілді өзгерту"
]))
async def handle_change_language(message: Message, state: FSMContext):
    """Handle change language button"""
    await message.answer(
        get_text('choose_language', 'ru'),
        reply_markup=get_language_keyboard()
    )


# Clear chat handler
@router.message(F.text.in_([
    "🗑 Очистить чат", "🗑 Чатты тазалау"
]))
async def handle_clear_chat(message: Message, state: FSMContext):
    """Handle clear chat button"""
    telegram_id = message.from_user.id
    lang = db.get_user_language(telegram_id)

    await state.clear()
    await message.answer(
        get_text('chat_cleared', lang),
        reply_markup=get_main_menu_keyboard(lang)
    )


# Main menu handler
@router.message(F.text.in_([
    "🏠 Главное меню", "🏠 Басты мәзір"
]))
async def handle_main_menu(message: Message, state: FSMContext):
    """Return to main menu"""
    await state.clear()
    telegram_id = message.from_user.id
    lang = db.get_user_language(telegram_id)
    await message.answer("🏠", reply_markup=get_main_menu_keyboard(lang))


# Ignore callback (for disabled buttons)
@router.callback_query(F.data == "ignore")
async def ignore_callback(callback: CallbackQuery):
    """Ignore callback (for disabled buttons)"""
    await callback.answer()


# Search back button
@router.callback_query(F.data == "search_back")
async def search_back(callback: CallbackQuery, state: FSMContext):
    """Back button from city selection"""
    await state.clear()
    telegram_id = callback.from_user.id
    lang = db.get_user_language(telegram_id)
    await callback.message.delete()
    await callback.message.answer("🏠", reply_markup=get_main_menu_keyboard(lang))
    await callback.answer()


# Filters back button
@router.callback_query(F.data == "filters_back")
async def filters_back(callback: CallbackQuery, state: FSMContext):
    """Back button from filters summary"""
    from .search import SearchStates
    
    telegram_id = callback.from_user.id
    lang = db.get_user_language(telegram_id)

    data = await state.get_data()
    filters = data.get('filters', {})

    if 'district_id' in filters:
        districts = db.get_districts(filters['city_id'])
        await callback.message.edit_text(
            get_text('select_district', lang),
            reply_markup=get_districts_keyboard(districts, lang)
        )
        await state.set_state(SearchStates.selecting_district)
    else:
        cities = db.get_cities()
        await callback.message.edit_text(
            get_text('select_city', lang),
            reply_markup=get_cities_keyboard(cities, lang)
        )
        await state.set_state(SearchStates.selecting_city)
    await callback.answer()


# Change filters
@router.callback_query(F.data == "change_filters")
async def change_filters(callback: CallbackQuery, state: FSMContext):
    """Change search filters"""
    from .search import SearchStates
    
    telegram_id = callback.from_user.id
    lang = db.get_user_language(telegram_id)

    cities = db.get_cities()
    await callback.message.edit_text(
        get_text('select_city', lang),
        reply_markup=get_cities_keyboard(cities, lang)
    )
    await state.set_state(SearchStates.selecting_city)
    await callback.answer()


# Clear all filters
@router.callback_query(F.data.in_(["clear_filters", "clear_all_filters"]))
async def clear_all_filters(callback: CallbackQuery, state: FSMContext):
    """Clear all filters"""
    from .search import SearchStates
    
    telegram_id = callback.from_user.id
    lang = db.get_user_language(telegram_id)

    await state.update_data(filters={})
    cities = db.get_cities()
    await callback.message.edit_text(
        get_text('select_city', lang),
        reply_markup=get_cities_keyboard(cities, lang)
    )
    await state.set_state(SearchStates.selecting_city)
    await callback.answer(get_text('filters_cleared', lang))
