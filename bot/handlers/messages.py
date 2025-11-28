"""
Messages handlers - chat between user and landlord
"""
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
from keyboards import get_main_menu_keyboard, get_message_reply_keyboard
from locales import get_text
from logger import setup_logger

router = Router()
logger = setup_logger('messages')


class MessageStates(StatesGroup):
    writing_message = State()


@router.callback_query(F.data.startswith("chat_"))
async def start_chat(callback: CallbackQuery, state: FSMContext):
    """Start chat with landlord/user"""
    booking_id = int(callback.data.split("_")[1])
    telegram_id = callback.from_user.id
    user = db.get_user(telegram_id)
    lang = user['language']

    # Validate booking
    booking = db.get_booking_by_id(booking_id)
    if not booking:
        await callback.answer(get_text('booking_not_found', lang), show_alert=True)
        return

    # Check user is part of this booking
    if booking['user_id'] != user['id'] and booking['landlord_id'] != user['id']:
        await callback.answer(get_text('booking_not_found', lang), show_alert=True)
        return

    # Show message history first
    messages = db.get_booking_messages(booking_id)
    
    if messages:
        title = booking['title_ru'] if lang == 'ru' else booking.get('title_kk', booking['title_ru'])
        text = get_text('messages_history', lang) + f"\n🏠 {title}\n\n"
        
        for msg in messages[-10:]:  # Last 10 messages
            sender = db.get_user_by_id(msg['sender_id'])
            sender_name = sender['full_name'] if sender else 'Unknown'
            time = msg['created_at'][:16] if msg['created_at'] else ''
            text += f"👤 {sender_name} ({time}):\n{msg['message']}\n\n"
        
        await callback.message.answer(text)
    
    # Store booking_id for message sending
    await state.update_data(chat_booking_id=booking_id)
    await callback.message.answer(get_text('enter_message', lang))
    await state.set_state(MessageStates.writing_message)
    await callback.answer()


@router.message(MessageStates.writing_message)
async def send_message(message: Message, state: FSMContext, bot: Bot):
    """Send message to landlord/user"""
    telegram_id = message.from_user.id
    user = db.get_user(telegram_id)
    lang = user['language']

    data = await state.get_data()
    booking_id = data.get('chat_booking_id')

    if not booking_id:
        await message.answer(get_text('error_occurred', lang), reply_markup=get_main_menu_keyboard(lang))
        await state.clear()
        return

    booking = db.get_booking_by_id(booking_id)
    if not booking:
        await message.answer(get_text('booking_not_found', lang), reply_markup=get_main_menu_keyboard(lang))
        await state.clear()
        return

    # Save message
    db.create_message(booking_id, user['id'], message.text)

    # Determine recipient
    if booking['user_id'] == user['id']:
        recipient_telegram_id = booking.get('landlord_telegram_id')
    else:
        recipient_telegram_id = booking.get('user_telegram_id')

    # Notify recipient
    if recipient_telegram_id:
        title = booking['title_ru'] if lang == 'ru' else booking.get('title_kk', booking['title_ru'])
        recipient_lang = db.get_user_language(recipient_telegram_id)
        
        notification = get_text('new_message_notification', recipient_lang,
            sender_name=user['full_name'],
            apartment_title=title,
            message=message.text[:200]
        )
        
        try:
            await bot.send_message(
                recipient_telegram_id,
                notification,
                reply_markup=get_message_reply_keyboard(booking_id, recipient_lang)
            )
        except Exception as e:
            logger.error(f"Failed to notify recipient {recipient_telegram_id}: {e}")

    await message.answer(get_text('message_sent', lang), reply_markup=get_main_menu_keyboard(lang))
    await state.clear()
