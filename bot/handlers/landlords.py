"""
Landlords handlers - landlord registration and management
"""
import re
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
from keyboards import get_landlord_menu_keyboard, get_main_menu_keyboard, get_back_keyboard
from locales import get_text
from utils import validate_phone

router = Router()


class LandlordStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_email = State()


@router.message(F.text.in_([
    "🏠 Арендодателям", "🏠 Жалға берушілерге"
]))
async def handle_landlords(message: Message, state: FSMContext):
    """Handle landlords section"""
    telegram_id = message.from_user.id
    lang = db.get_user_language(telegram_id)

    await message.answer(
        get_text('landlords_menu', lang),
        reply_markup=get_landlord_menu_keyboard(lang)
    )


@router.message(F.text.in_([
    "📋 Условия сотрудничества", "📋 Ынтымақтастық шарттары"
]))
async def handle_conditions(message: Message):
    """Show landlord conditions"""
    telegram_id = message.from_user.id
    lang = db.get_user_language(telegram_id)
    await message.answer(get_text('conditions_text', lang))


@router.message(F.text.in_([
    "📝 Подключиться", "📝 Қосылу"
]))
async def handle_connect(message: Message, state: FSMContext):
    """Start landlord connection process"""
    telegram_id = message.from_user.id
    lang = db.get_user_language(telegram_id)

    await message.answer(
        get_text('enter_landlord_name', lang),
        reply_markup=get_back_keyboard(lang)
    )
    await state.set_state(LandlordStates.waiting_for_name)


@router.message(LandlordStates.waiting_for_name)
async def process_landlord_name(message: Message, state: FSMContext):
    """Handle landlord name input"""
    telegram_id = message.from_user.id
    lang = db.get_user_language(telegram_id)

    if message.text in [get_text('btn_back', lang), get_text('btn_main_menu', lang)]:
        await state.clear()
        await message.answer(
            get_text('landlords_menu', lang),
            reply_markup=get_landlord_menu_keyboard(lang)
        )
        return

    await state.update_data(landlord_name=message.text.strip())
    await message.answer(get_text('enter_landlord_phone', lang))
    await state.set_state(LandlordStates.waiting_for_phone)


@router.message(LandlordStates.waiting_for_phone)
async def process_landlord_phone(message: Message, state: FSMContext):
    """Handle landlord phone input"""
    telegram_id = message.from_user.id
    lang = db.get_user_language(telegram_id)

    if message.text in [get_text('btn_back', lang), get_text('btn_main_menu', lang)]:
        await state.clear()
        await message.answer(
            get_text('landlords_menu', lang),
            reply_markup=get_landlord_menu_keyboard(lang)
        )
        return

    phone = message.text.strip()
    if not validate_phone(phone):
        await message.answer(get_text('invalid_phone', lang))
        return

    await state.update_data(landlord_phone=phone)
    await message.answer(get_text('enter_landlord_email', lang))
    await state.set_state(LandlordStates.waiting_for_email)


@router.message(LandlordStates.waiting_for_email)
async def process_landlord_email(message: Message, state: FSMContext):
    """Handle landlord email input"""
    telegram_id = message.from_user.id
    lang = db.get_user_language(telegram_id)

    if message.text in [get_text('btn_back', lang), get_text('btn_main_menu', lang)]:
        await state.clear()
        await message.answer(
            get_text('landlords_menu', lang),
            reply_markup=get_landlord_menu_keyboard(lang)
        )
        return

    email = message.text.strip()
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        await message.answer(get_text('invalid_email', lang))
        return

    data = await state.get_data()
    db.create_landlord_request(telegram_id, data['landlord_name'], data['landlord_phone'], email)

    await state.clear()
    await message.answer(
        get_text('connect_request_sent', lang),
        reply_markup=get_main_menu_keyboard(lang)
    )
