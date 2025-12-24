"""
Search handlers - apartment search flow
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
from keyboards import (
    get_cities_keyboard, get_districts_keyboard, get_main_menu_keyboard,
    get_search_filters_keyboard, get_apartment_card_keyboard, get_no_apartments_keyboard
)
from locales import get_text
from utils import format_apartment_card, send_apartment_card

router = Router()


class SearchStates(StatesGroup):
    selecting_city = State()
    selecting_district = State()
    viewing_apartments = State()


@router.message(F.text.in_([
    "🔍 Поиск", "🔍 Іздеу"
]))
async def handle_search(message: Message, state: FSMContext):
    """Handle search button"""
    telegram_id = message.from_user.id
    lang = db.get_user_language(telegram_id)

    cities = db.get_cities()
    await message.answer(
        get_text('select_city', lang),
        reply_markup=get_cities_keyboard(cities, lang)
    )
    await state.set_state(SearchStates.selecting_city)
    await state.update_data(filters={})


@router.callback_query(F.data.startswith("city_"))
async def process_city_selection(callback: CallbackQuery, state: FSMContext):
    """Handle city selection"""
    city_id = int(callback.data.split("_")[1])
    telegram_id = callback.from_user.id
    lang = db.get_user_language(telegram_id)

    data = await state.get_data()
    filters = data.get('filters', {})
    filters['city_id'] = city_id
    await state.update_data(filters=filters)

    districts = db.get_districts(city_id)
    
    # Remove keyboard from current message
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    
    await callback.message.answer(
        get_text('select_district', lang),
        reply_markup=get_districts_keyboard(districts, lang)
    )
    await state.set_state(SearchStates.selecting_district)
    await callback.answer()


@router.callback_query(F.data.startswith("district_"))
async def process_district_selection(callback: CallbackQuery, state: FSMContext):
    """Handle district selection"""
    if callback.data == "district_back":
        telegram_id = callback.from_user.id
        lang = db.get_user_language(telegram_id)
        cities = db.get_cities()
        
        # Remove keyboard from current message
        try:
            await callback.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass
        
        await callback.message.answer(
            get_text('select_city', lang),
            reply_markup=get_cities_keyboard(cities, lang)
        )
        await state.set_state(SearchStates.selecting_city)
        await callback.answer()
        return

    telegram_id = callback.from_user.id
    lang = db.get_user_language(telegram_id)

    data = await state.get_data()
    filters = data.get('filters', {})

    if callback.data == "district_all":
        filters['district_id'] = None
    else:
        district_id = int(callback.data.split("_")[1])
        filters['district_id'] = district_id

    # Remove keyboard from current message
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    await state.update_data(filters=filters)
    await show_filters_summary(callback.message, filters, lang, is_new_message=True)
    await state.set_state(SearchStates.viewing_apartments)
    await callback.answer()


async def show_filters_summary(message, filters: dict, lang: str, is_new_message: bool = False):
    """Show active filters summary"""
    if 'city_id' not in filters:
        # State was reset, redirect to search
        cities = db.get_cities()
        if is_new_message:
            await message.answer(
                get_text('select_city', lang),
                reply_markup=get_cities_keyboard(cities, lang)
            )
        else:
            await message.edit_text(
                get_text('select_city', lang),
                reply_markup=get_cities_keyboard(cities, lang)
            )
        return
    
    city = db.get_city_by_id(filters['city_id'])
    city_name = city['name_ru'] if lang == 'ru' else city['name_kk']

    if filters.get('district_id') is None:
        district_name = get_text('all_districts', lang)
    else:
        district = db.get_district_by_id(filters['district_id'])
        district_name = district['name_ru'] if lang == 'ru' else district['name_kk']

    text = get_text('active_filters_no_dates', lang,
                    city=city_name,
                    district=district_name)

    apartments = db.get_apartments(
        city_id=filters['city_id'],
        district_id=filters.get('district_id')
    )
    count = len(apartments)

    if is_new_message:
        await message.answer(
            text,
            reply_markup=get_search_filters_keyboard(filters, count, lang)
        )
    else:
        await message.edit_text(
            text,
            reply_markup=get_search_filters_keyboard(filters, count, lang)
        )


@router.callback_query(F.data == "show_apartments")
async def show_apartments(callback: CallbackQuery, state: FSMContext):
    """Show available apartments"""
    telegram_id = callback.from_user.id
    user = db.get_user(telegram_id)
    lang = user['language']

    data = await state.get_data()
    filters = data.get('filters', {})

    apartments = db.get_apartments(
        city_id=filters.get('city_id'),
        district_id=filters.get('district_id')
    )

    if not apartments:
        await callback.message.edit_text(
            get_text('no_apartments', lang),
            reply_markup=get_no_apartments_keyboard(lang)
        )
        await callback.answer()
        return

    await state.update_data(apartments=apartments, apt_index=0)
    await callback.message.delete()
    await show_apartment(callback.message, state, 0, user)
    await callback.answer()


async def show_apartment(message: Message, state: FSMContext, index: int, user: dict):
    """Show apartment card by index"""
    data = await state.get_data()
    apartments = data.get('apartments', [])

    if not apartments or index < 0 or index >= len(apartments):
        return

    # Delete previous apartment messages
    prev_message_ids = data.get('apartment_message_ids', [])
    for msg_id in prev_message_ids:
        try:
            await message.bot.delete_message(message.chat.id, msg_id)
        except Exception:
            pass  # Message already deleted or too old

    apartment = apartments[index]
    lang = user['language']

    has_prev = index > 0
    has_next = index < len(apartments) - 1
    is_fav = db.is_favorite(user['id'], apartment['id'])

    keyboard = get_apartment_card_keyboard(
        apartment['id'],
        is_favorite=is_fav,
        lang=lang,
        has_prev=has_prev,
        has_next=has_next
    )

    await send_apartment_card(message, apartment, keyboard, lang, user['id'], state)
    await state.update_data(apt_index=index)


@router.callback_query(F.data.startswith("apt_"))
async def navigate_apartments(callback: CallbackQuery, state: FSMContext):
    """Navigate through apartments"""
    direction = callback.data.split("_")[1]
    data = await state.get_data()
    current_index = data.get('apt_index', 0)

    if direction == "prev":
        new_index = current_index - 1
    else:
        new_index = current_index + 1

    telegram_id = callback.from_user.id
    user = db.get_user(telegram_id)

    await show_apartment(callback.message, state, new_index, user)
    await callback.answer()
