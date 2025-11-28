"""
Registration handlers - user registration flow
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
from keyboards import get_language_keyboard, get_main_menu_keyboard, get_back_keyboard
from locales import get_text
from logger import setup_logger, get_audit_logger, log_user_action
from utils import validate_phone

router = Router()
logger = setup_logger('registration')
audit_logger = get_audit_logger()


class RegistrationStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command"""
    await state.clear()
    telegram_id = message.from_user.id
    user = db.get_user(telegram_id)

    if not user:
        await message.answer(
            get_text('choose_language', 'ru'),
            reply_markup=get_language_keyboard()
        )
    else:
        lang = user['language']
        if user['full_name']:
            await message.answer(
                get_text('welcome_back', lang, name=user['full_name']),
                reply_markup=get_main_menu_keyboard(lang)
            )
        else:
            await message.answer(
                get_text('enter_full_name', lang),
                reply_markup=get_back_keyboard(lang)
            )
            await state.set_state(RegistrationStates.waiting_for_name)


@router.callback_query(F.data.startswith("lang_"))
async def process_language_selection(callback: CallbackQuery, state: FSMContext):
    """Handle language selection"""
    lang = callback.data.split("_")[1]
    telegram_id = callback.from_user.id

    user = db.get_user(telegram_id)
    if not user:
        db.create_user(telegram_id, callback.from_user.username, lang)
    else:
        db.update_user(telegram_id, language=lang)

    await callback.message.edit_text(get_text('language_set', lang))
    await callback.message.answer(get_text('welcome', lang))
    await callback.message.answer(
        get_text('enter_full_name', lang),
        reply_markup=get_back_keyboard(lang)
    )
    await state.set_state(RegistrationStates.waiting_for_name)
    await callback.answer()


@router.message(RegistrationStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    """Handle full name input"""
    telegram_id = message.from_user.id
    lang = db.get_user_language(telegram_id)

    if message.text == get_text('btn_back', lang) or message.text == get_text('btn_main_menu', lang):
        await state.clear()
        await message.answer(
            get_text('choose_language', lang),
            reply_markup=get_language_keyboard()
        )
        return

    full_name = message.text.strip()
    if len(full_name) < 3:
        await message.answer(get_text('enter_full_name', lang))
        return

    db.update_user(telegram_id, full_name=full_name)
    await message.answer(
        get_text('enter_phone', lang),
        reply_markup=get_back_keyboard(lang)
    )
    await state.set_state(RegistrationStates.waiting_for_phone)


@router.message(RegistrationStates.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    """Handle phone number input"""
    telegram_id = message.from_user.id
    lang = db.get_user_language(telegram_id)

    if message.text == get_text('btn_back', lang):
        await message.answer(
            get_text('enter_full_name', lang),
            reply_markup=get_back_keyboard(lang)
        )
        await state.set_state(RegistrationStates.waiting_for_name)
        return

    if message.text == get_text('btn_main_menu', lang):
        await state.clear()
        user = db.get_user(telegram_id)
        await message.answer(
            get_text('welcome_back', lang, name=user['full_name']),
            reply_markup=get_main_menu_keyboard(lang)
        )
        return

    phone = message.text.strip()
    if not validate_phone(phone):
        await message.answer(get_text('invalid_phone', lang))
        return

    db.update_user(telegram_id, phone=phone)
    user = db.get_user(telegram_id)

    log_user_action(logger, telegram_id, "Registration completed", f"Phone: {phone}")
    audit_logger.info(f"New user registered: {telegram_id}")

    await state.clear()
    await message.answer(
        get_text('registration_complete', lang, name=user['full_name']),
        reply_markup=get_main_menu_keyboard(lang)
    )
