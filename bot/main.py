import asyncio
import logging
import re
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

import database as db
from keyboards import *
from locales import get_text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
BOT_TOKEN = "8598342556:AAGdy5OpK3qJaYYtsqkmX_BPrHDJf5XuDNI"  # Set your token here
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()

# FSM States
class RegistrationStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()

class SearchStates(StatesGroup):
    selecting_city = State()
    selecting_district = State()
    viewing_apartments = State()

class BookingStates(StatesGroup):
    confirming = State()
    waiting_contact = State()

class LandlordStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_email = State()

class ReviewStates(StatesGroup):
    selecting_rating = State()
    writing_comment = State()

# Phone validation regex
PHONE_REGEX = r'^\+7\s?\(?\d{3}\)?\s?\d{3}\s?\d{2}\s?\d{2}$'

def validate_phone(phone: str) -> bool:
    """Validate phone number format

    Supported formats:
    - +7 (XXX) XXX XX XX
    - +7 XXX XXX XX XX
    - 7 XXX XXX XX XX
    - 8 XXX XXX XX XX
    """
    # Remove spaces, parentheses, and hyphens
    cleaned = re.sub(r'[\s\(\)\-]', '', phone)

    # Replace 8 with 7 at the beginning
    if cleaned.startswith('8'):
        cleaned = '7' + cleaned[1:]

    # Add + if not present
    if not cleaned.startswith('+'):
        cleaned = '+' + cleaned

    # Check if matches +7XXXXXXXXXX (11 digits total)
    return bool(re.match(r'^\+7\d{10}$', cleaned))

def format_price(price: float) -> str:
    """Format price with thousands separator"""
    return "{:,.0f}".format(price).replace(',', ' ')

def format_apartment_card(apartment: dict, lang: str = 'ru') -> str:
    """Format apartment information as text"""
    name_key = 'name_ru' if lang == 'ru' else 'name_kk'
    title_key = 'title_ru' if lang == 'ru' else 'title_kk'
    desc_key = 'description_ru' if lang == 'ru' else 'description_kk'

    text = f"🏠 *{apartment[title_key]}*\n\n"

    if apartment.get('promotion'):
        text += f"🎁 {apartment['promotion']}\n\n"

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

# Command handlers
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command"""
    await state.clear()
    telegram_id = message.from_user.id
    user = db.get_user(telegram_id)

    if not user:
        # New user - show language selection
        await message.answer(
            get_text('choose_language', 'ru'),
            reply_markup=get_language_keyboard()
        )
    else:
        # Returning user
        lang = user['language']
        if user['full_name']:
            await message.answer(
                get_text('welcome_back', lang, name=user['full_name']),
                reply_markup=get_main_menu_keyboard(lang)
            )
        else:
            # Incomplete registration
            await message.answer(
                get_text('enter_full_name', lang),
                reply_markup=get_back_keyboard(lang)
            )
            await state.set_state(RegistrationStates.waiting_for_name)

# Language selection
@router.callback_query(F.data.startswith("lang_"))
async def process_language_selection(callback: CallbackQuery, state: FSMContext):
    """Handle language selection"""
    lang = callback.data.split("_")[1]
    telegram_id = callback.from_user.id

    user = db.get_user(telegram_id)
    if not user:
        db.create_user(telegram_id, callback.from_user.username, lang)
        user = db.get_user(telegram_id)
    else:
        db.update_user(telegram_id, language=lang)

    await callback.message.edit_text(get_text('language_set', lang))

    # Show welcome and ask for registration
    await callback.message.answer(get_text('welcome', lang))
    await callback.message.answer(
        get_text('enter_full_name', lang),
        reply_markup=get_back_keyboard(lang)
    )
    await state.set_state(RegistrationStates.waiting_for_name)
    await callback.answer()

# Registration handlers
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

    await state.clear()
    await message.answer(
        get_text('registration_complete', lang, name=user['full_name']),
        reply_markup=get_main_menu_keyboard(lang)
    )

# Main menu handlers
@router.message(F.text.in_([
    get_text('btn_search', 'ru'), get_text('btn_search', 'kk')
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

@router.message(F.text.in_([
    get_text('btn_history', 'ru'), get_text('btn_history', 'kk')
]))
async def handle_history(message: Message, state: FSMContext):
    """Handle history button"""
    telegram_id = message.from_user.id
    user = db.get_user(telegram_id)
    lang = user['language']

    bookings = db.get_user_bookings(user['id'])

    if not bookings:
        await message.answer(get_text('history_empty', lang))
        return

    await message.answer(get_text('history_title', lang))

    for booking in bookings[:10]:  # Show last 10
        status_key = f"status_{booking['status']}"
        title = booking['title_ru'] if lang == 'ru' else booking['title_kk']

        text = f"🏠 *{title}*\n"
        text += f"📍 {booking['address']}\n"
        text += f"📅 {booking['check_in_date']} - {booking['check_out_date']}\n"
        text += f"💰 {format_price(booking['total_price'])} ₸\n"
        text += f"{get_text(status_key, lang)}"

        await message.answer(text, parse_mode="Markdown")

@router.message(F.text.in_([
    get_text('btn_favorites', 'ru'), get_text('btn_favorites', 'kk')
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

    # Show first apartment
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

    text = format_apartment_card(apartment, lang)

    has_prev = index > 0
    has_next = index < len(favorites) - 1

    keyboard = get_apartment_card_keyboard(
        apartment['id'],
        is_favorite=True,
        lang=lang,
        has_prev=has_prev,
        has_next=has_next
    )

    if apartment.get('photos'):
        photo_path = apartment['photos'][0]
        try:
            photo = FSInputFile(photo_path)
            await message.answer_photo(photo, caption=text, parse_mode="Markdown", reply_markup=keyboard)
        except Exception:
            await message.answer(text, parse_mode="Markdown", reply_markup=keyboard)
    else:
        await message.answer(text, parse_mode="Markdown", reply_markup=keyboard)

    await state.update_data(fav_index=index)

@router.message(F.text.in_([
    get_text('btn_language', 'ru'), get_text('btn_language', 'kk')
]))
async def handle_change_language(message: Message, state: FSMContext):
    """Handle change language button"""
    await message.answer(
        get_text('choose_language', 'ru'),
        reply_markup=get_language_keyboard()
    )

@router.message(F.text.in_([
    get_text('btn_landlords', 'ru'), get_text('btn_landlords', 'kk')
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
    get_text('btn_conditions', 'ru'), get_text('btn_conditions', 'kk')
]))
async def handle_conditions(message: Message):
    """Show landlord conditions"""
    telegram_id = message.from_user.id
    lang = db.get_user_language(telegram_id)
    await message.answer(get_text('conditions_text', lang))

@router.message(F.text.in_([
    get_text('btn_connect', 'ru'), get_text('btn_connect', 'kk')
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
    # Validate email format
    import re
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

@router.message(F.text.in_([
    get_text('btn_main_menu', 'ru'), get_text('btn_main_menu', 'kk')
]))
async def handle_main_menu(message: Message, state: FSMContext):
    """Return to main menu"""
    await state.clear()
    telegram_id = message.from_user.id
    lang = db.get_user_language(telegram_id)
    await message.answer("🏠", reply_markup=get_main_menu_keyboard(lang))

# Search callback handlers
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
    await callback.message.edit_text(
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
        await callback.message.edit_text(
            get_text('select_city', lang),
            reply_markup=get_cities_keyboard(cities, lang)
        )
        await state.set_state(SearchStates.selecting_city)
        await callback.answer()
        return

    district_id = int(callback.data.split("_")[1])
    telegram_id = callback.from_user.id
    lang = db.get_user_language(telegram_id)

    data = await state.get_data()
    filters = data.get('filters', {})
    filters['district_id'] = district_id
    await state.update_data(filters=filters)

    # Show filters summary and available apartments
    await show_filters_summary(callback.message, filters, lang)
    await state.set_state(SearchStates.viewing_apartments)
    await callback.answer()


async def show_filters_summary(message, filters: dict, lang: str):
    """Show active filters summary"""
    city = db.get_city_by_id(filters['city_id'])
    district = db.get_district_by_id(filters['district_id'])

    city_name = city['name_ru'] if lang == 'ru' else city['name_kk']
    district_name = district['name_ru'] if lang == 'ru' else district['name_kk']

    text = get_text('active_filters_no_dates', lang,
                    city=city_name,
                    district=district_name)

    # Count available apartments
    apartments = db.get_apartments(
        city_id=filters['city_id'],
        district_id=filters['district_id']
    )
    count = len(apartments)

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

    apartment = apartments[index]
    lang = user['language']

    text = format_apartment_card(apartment, lang)

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

    if apartment.get('photos'):
        photo_path = apartment['photos'][0]
        try:
            photo = FSInputFile(photo_path)
            await message.answer_photo(photo, caption=text, parse_mode="Markdown", reply_markup=keyboard)
        except Exception:
            await message.answer(text, parse_mode="Markdown", reply_markup=keyboard)
    else:
        await message.answer(text, parse_mode="Markdown", reply_markup=keyboard)

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

    await callback.message.delete()
    await show_apartment(callback.message, state, new_index, user)
    await callback.answer()

@router.callback_query(F.data.startswith("fav_"))
async def add_to_favorites(callback: CallbackQuery, state: FSMContext):
    """Add apartment to favorites"""
    apartment_id = int(callback.data.split("_")[1])
    telegram_id = callback.from_user.id
    user = db.get_user(telegram_id)
    lang = user['language']

    db.add_to_favorites(user['id'], apartment_id)
    await callback.answer(get_text('added_to_favorites', lang))

    # Update keyboard
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

    db.remove_from_favorites(user['id'], apartment_id)
    await callback.answer(get_text('removed_from_favorites', lang))

    # Update keyboard
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

@router.callback_query(F.data.startswith("book_"))
async def start_booking(callback: CallbackQuery, state: FSMContext):
    """Start booking process"""
    apartment_id = int(callback.data.split("_")[1])
    telegram_id = callback.from_user.id
    user = db.get_user(telegram_id)
    lang = user['language']

    data = await state.get_data()
    filters = data.get('filters', {})

    # Check availability
    if not db.check_apartment_availability(apartment_id, filters.get('check_in'), filters.get('check_out')):
        await callback.answer(get_text('apartment_booked', lang), show_alert=True)
        return

    await state.update_data(booking_apartment_id=apartment_id)

    # If user has phone, create booking directly
    if user.get('phone'):
        await create_booking_request(callback.message, state, user)
    else:
        # Request contact
        await callback.message.answer(
            get_text('enter_phone', lang),
            reply_markup=get_contact_keyboard(lang)
        )
        await state.set_state(BookingStates.waiting_contact)

    await callback.answer()

async def create_booking_request(message: Message, state: FSMContext, user: dict):
    """Create booking request"""
    data = await state.get_data()
    apartment_id = data.get('booking_apartment_id')
    filters = data.get('filters', {})
    lang = user['language']

    apartment = db.get_apartment_by_id(apartment_id)

    # Calculate price
    check_in = datetime.strptime(filters['check_in'], "%Y-%m-%d")
    check_out = datetime.strptime(filters['check_out'], "%Y-%m-%d")
    days = (check_out - check_in).days
    total_price = apartment['price_per_day'] * days

    # Platform fee (5%)
    fee_percent = float(db.get_setting('platform_fee_percent') or 5)
    platform_fee = total_price * (fee_percent / 100)

    # Create booking
    booking_id = db.create_booking(
        user['id'], apartment_id, apartment['landlord_id'],
        filters['check_in'], filters['check_out'],
        total_price, platform_fee
    )

    await message.answer(
        get_text('booking_created', lang),
        reply_markup=get_main_menu_keyboard(lang)
    )

    # TODO: Notify landlord about new booking

    await state.clear()

@router.message(BookingStates.waiting_contact, F.contact)
async def process_contact(message: Message, state: FSMContext):
    """Handle contact sharing"""
    telegram_id = message.from_user.id
    user = db.get_user(telegram_id)
    lang = user['language']

    phone = message.contact.phone_number
    if not phone.startswith('+'):
        phone = '+' + phone

    db.update_user(telegram_id, phone=phone)
    user = db.get_user(telegram_id)

    await create_booking_request(message, state, user)

@router.callback_query(F.data == "clear_filters")
async def clear_filters(callback: CallbackQuery, state: FSMContext):
    """Clear all search filters"""
    telegram_id = callback.from_user.id
    lang = db.get_user_language(telegram_id)

    await state.update_data(filters={})
    await callback.answer(get_text('filters_cleared', lang))

    cities = db.get_cities()
    await callback.message.edit_text(
        get_text('select_city', lang),
        reply_markup=get_cities_keyboard(cities, lang)
    )
    await state.set_state(SearchStates.selecting_city)

@router.callback_query(F.data.startswith("reviews_"))
async def show_reviews(callback: CallbackQuery, state: FSMContext):
    """Show apartment reviews"""
    apartment_id = int(callback.data.split("_")[1])
    telegram_id = callback.from_user.id
    lang = db.get_user_language(telegram_id)

    reviews = db.get_apartment_reviews(apartment_id, limit=5)

    if not reviews:
        await callback.answer(get_text('no_reviews', lang), show_alert=True)
        return

    text = get_text('reviews_title', lang) + "\n\n"

    for review in reviews:
        stars = "⭐" * review['rating']
        text += f"{stars} {review['rating']}.0\n"
        text += f"👤 {review['user_name']}\n"
        text += f"📅 {review['created_at'][:10]}\n\n"
        if review.get('comment'):
            text += f"{review['comment']}\n\n"
        text += f"👍 {review['helpful_count']} | 👎 {review['not_helpful_count']}\n"
        text += "─" * 20 + "\n\n"

    await callback.message.answer(text)
    await callback.answer()

@router.callback_query(F.data == "ignore")
async def ignore_callback(callback: CallbackQuery):
    """Ignore callback (for disabled buttons)"""
    await callback.answer()

# Main function
async def main():
    """Start bot"""
    # Initialize database
    db.init_db()

    # Include router
    dp.include_router(router)

    # Start polling
    logger.info("Starting bot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
