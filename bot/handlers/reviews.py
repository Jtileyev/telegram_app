"""
Reviews handlers - review management
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
from keyboards import get_reviews_pagination_keyboard, get_rating_keyboard, get_skip_comment_keyboard, get_main_menu_keyboard
from locales import get_text
from constants import REVIEWS_PER_PAGE, MIN_REVIEW_COMMENT_LENGTH

router = Router()


class ReviewStates(StatesGroup):
    selecting_rating = State()
    rating_cleanliness = State()
    rating_accuracy = State()
    rating_communication = State()
    rating_location = State()
    writing_comment = State()


@router.callback_query(F.data.startswith("start_review_"))
async def start_review(callback: CallbackQuery, state: FSMContext):
    """Start review process from booking history"""
    booking_id = int(callback.data.split("_")[2])
    telegram_id = callback.from_user.id
    user = db.get_user(telegram_id)
    lang = user['language']

    # Verify user can leave review
    if not db.can_leave_review(user['id'], booking_id):
        await callback.answer(get_text('already_reviewed', lang), show_alert=True)
        return

    # Get booking details
    booking = db.get_booking_by_id(booking_id)
    if not booking:
        await callback.answer(get_text('booking_not_found', lang), show_alert=True)
        return

    # Store booking info in state
    await state.update_data(
        review_booking_id=booking_id,
        review_apartment_id=booking['apartment_id']
    )

    title = booking['title_ru'] if lang == 'ru' else booking.get('title_kk', booking['title_ru'])
    prompt_text = get_text('review_prompt', lang) + f"\n\n🏠 {title}\n📍 {booking['address']}\n\n"
    prompt_text += get_text('select_rating', lang)

    await callback.message.answer(prompt_text, reply_markup=get_rating_keyboard(lang))
    await state.set_state(ReviewStates.selecting_rating)
    await callback.answer()


@router.callback_query(F.data.startswith("reviews_"))
async def show_reviews(callback: CallbackQuery, state: FSMContext):
    """Show apartment reviews"""
    if callback.data.startswith("reviews_page_"):
        return  # Handled by reviews_pagination

    apartment_id = int(callback.data.split("_")[1])
    telegram_id = callback.from_user.id
    lang = db.get_user_language(telegram_id)

    # Validate apartment exists
    apartment = db.get_apartment_by_id(apartment_id)
    if not apartment:
        await callback.answer(get_text('apartment_not_found', lang), show_alert=True)
        return

    reviews = db.get_apartment_reviews(apartment_id, limit=REVIEWS_PER_PAGE)

    if not reviews:
        await callback.answer(get_text('no_reviews', lang), show_alert=True)
        return

    text = get_text('reviews_title', lang) + "\n\n"

    for review in reviews:
        stars = "⭐" * review['rating']
        text += f"{stars} {review['rating']}.0\n"
        text += f"👤 {review['user_name']}\n"
        text += f"📅 {review['created_at'][:10]}\n"
        # Show detailed ratings if available
        if any([review.get('cleanliness_rating'), review.get('accuracy_rating'),
                review.get('communication_rating'), review.get('location_rating')]):
            text += get_text('detailed_ratings', lang,
                cleanliness=review.get('cleanliness_rating') or '-',
                accuracy=review.get('accuracy_rating') or '-',
                communication=review.get('communication_rating') or '-',
                location=review.get('location_rating') or '-'
            ) + "\n"
        text += "\n"
        if review.get('comment'):
            text += f"{review['comment']}\n\n"
        if review.get('landlord_reply'):
            text += f"{get_text('landlord_reply', lang)}\n{review['landlord_reply']}\n\n"
        text += f"👍 {review['helpful_count']} | 👎 {review['not_helpful_count']}\n"
        text += "─" * 20 + "\n\n"

    await callback.message.answer(text)
    await callback.answer()


@router.callback_query(F.data.startswith("rating_"))
async def select_rating(callback: CallbackQuery, state: FSMContext):
    """Select review rating"""
    from keyboards import get_detailed_rating_keyboard

    telegram_id = callback.from_user.id
    user = db.get_user(telegram_id)
    lang = user['language']

    # Get booking_id from state data
    data = await state.get_data()
    booking_id = data.get('review_booking_id')

    # Verify user can leave review for this booking
    if booking_id and not db.can_leave_review(user['id'], booking_id):
        await callback.answer(get_text('cannot_leave_review', lang), show_alert=True)
        await state.clear()
        return

    rating = int(callback.data.split("_")[1])

    await state.update_data(review_rating=rating)
    await callback.message.edit_text(get_text('rating_selected', lang, rating=rating))

    # Start detailed ratings flow
    await callback.message.answer(
        get_text('rate_cleanliness', lang),
        reply_markup=get_detailed_rating_keyboard('cleanliness', lang)
    )
    await state.set_state(ReviewStates.rating_cleanliness)
    await callback.answer()


@router.callback_query(F.data.startswith("detail_cleanliness_"))
async def rate_cleanliness(callback: CallbackQuery, state: FSMContext):
    """Rate cleanliness"""
    from keyboards import get_detailed_rating_keyboard

    telegram_id = callback.from_user.id
    lang = db.get_user_language(telegram_id)

    rating = int(callback.data.split("_")[2])
    await state.update_data(cleanliness_rating=rating)

    await callback.message.edit_text(f"🧹 {rating}/5")
    await callback.message.answer(
        get_text('rate_accuracy', lang),
        reply_markup=get_detailed_rating_keyboard('accuracy', lang)
    )
    await state.set_state(ReviewStates.rating_accuracy)
    await callback.answer()


@router.callback_query(F.data.startswith("detail_accuracy_"))
async def rate_accuracy(callback: CallbackQuery, state: FSMContext):
    """Rate accuracy"""
    from keyboards import get_detailed_rating_keyboard

    telegram_id = callback.from_user.id
    lang = db.get_user_language(telegram_id)

    rating = int(callback.data.split("_")[2])
    await state.update_data(accuracy_rating=rating)

    await callback.message.edit_text(f"📝 {rating}/5")
    await callback.message.answer(
        get_text('rate_communication', lang),
        reply_markup=get_detailed_rating_keyboard('communication', lang)
    )
    await state.set_state(ReviewStates.rating_communication)
    await callback.answer()


@router.callback_query(F.data.startswith("detail_communication_"))
async def rate_communication(callback: CallbackQuery, state: FSMContext):
    """Rate communication"""
    from keyboards import get_detailed_rating_keyboard

    telegram_id = callback.from_user.id
    lang = db.get_user_language(telegram_id)

    rating = int(callback.data.split("_")[2])
    await state.update_data(communication_rating=rating)

    await callback.message.edit_text(f"💬 {rating}/5")
    await callback.message.answer(
        get_text('rate_location', lang),
        reply_markup=get_detailed_rating_keyboard('location', lang)
    )
    await state.set_state(ReviewStates.rating_location)
    await callback.answer()


@router.callback_query(F.data.startswith("detail_location_"))
async def rate_location(callback: CallbackQuery, state: FSMContext):
    """Rate location - last detailed rating, proceed to comment"""
    telegram_id = callback.from_user.id
    lang = db.get_user_language(telegram_id)

    rating = int(callback.data.split("_")[2])
    await state.update_data(location_rating=rating)

    await callback.message.edit_text(f"📍 {rating}/5")
    await callback.message.answer(
        get_text('enter_review_comment', lang),
        reply_markup=get_skip_comment_keyboard(lang)
    )
    await state.set_state(ReviewStates.writing_comment)
    await callback.answer()


@router.callback_query(F.data == "skip_detailed_ratings")
async def skip_detailed_ratings(callback: CallbackQuery, state: FSMContext):
    """Skip all remaining detailed ratings and go to comment"""
    telegram_id = callback.from_user.id
    lang = db.get_user_language(telegram_id)

    await callback.message.edit_text("⏭")
    await callback.message.answer(
        get_text('enter_review_comment', lang),
        reply_markup=get_skip_comment_keyboard(lang)
    )
    await state.set_state(ReviewStates.writing_comment)
    await callback.answer()


@router.message(ReviewStates.writing_comment)
async def save_review_comment(message: Message, state: FSMContext):
    """Save review with comment"""
    telegram_id = message.from_user.id
    user = db.get_user(telegram_id)
    lang = user['language']

    data = await state.get_data()
    booking_id = data.get('review_booking_id')
    apartment_id = data.get('review_apartment_id')
    rating = data.get('review_rating')

    # Validate comment length
    comment = message.text.strip()
    if len(comment) < MIN_REVIEW_COMMENT_LENGTH:
        await message.answer(get_text('comment_too_short', lang))
        return

    # Verify user can still leave review
    if not db.can_leave_review(user['id'], booking_id):
        await message.answer(
            get_text('already_reviewed', lang),
            reply_markup=get_main_menu_keyboard(lang)
        )
        await state.clear()
        return

    # Save review with detailed ratings
    try:
        db.create_review(
            user_id=user['id'],
            apartment_id=apartment_id,
            booking_id=booking_id,
            rating=rating,
            comment=comment,
            cleanliness=data.get('cleanliness_rating'),
            accuracy=data.get('accuracy_rating'),
            communication=data.get('communication_rating'),
            location=data.get('location_rating')
        )
        await message.answer(
            get_text('review_submitted', lang),
            reply_markup=get_main_menu_keyboard(lang)
        )
    except Exception as e:
        await message.answer(
            get_text('error_occurred', lang),
            reply_markup=get_main_menu_keyboard(lang)
        )

    await state.clear()


@router.callback_query(F.data == "skip_review_comment")
async def skip_review_comment(callback: CallbackQuery, state: FSMContext):
    """Skip comment and save review without it"""
    telegram_id = callback.from_user.id
    user = db.get_user(telegram_id)
    lang = user['language']

    data = await state.get_data()
    booking_id = data.get('review_booking_id')
    apartment_id = data.get('review_apartment_id')
    rating = data.get('review_rating')

    # Verify user can still leave review
    if not db.can_leave_review(user['id'], booking_id):
        await callback.message.edit_text(get_text('already_reviewed', lang))
        await state.clear()
        await callback.answer()
        return

    # Save review without comment but with detailed ratings
    try:
        db.create_review(
            user_id=user['id'],
            apartment_id=apartment_id,
            booking_id=booking_id,
            rating=rating,
            comment=None,
            cleanliness=data.get('cleanliness_rating'),
            accuracy=data.get('accuracy_rating'),
            communication=data.get('communication_rating'),
            location=data.get('location_rating')
        )
        await callback.message.edit_text(get_text('review_submitted', lang))
    except Exception as e:
        await callback.message.edit_text(get_text('error_occurred', lang))

    await state.clear()
    await callback.answer()


@router.callback_query(F.data.startswith("helpful_"))
async def mark_helpful(callback: CallbackQuery):
    """Mark review as helpful"""
    review_id = int(callback.data.split("_")[1])
    telegram_id = callback.from_user.id
    lang = db.get_user_language(telegram_id)

    db.increment_review_helpful_count(review_id)

    await callback.answer(get_text('marked_helpful', lang))


@router.callback_query(F.data.startswith("not_helpful_"))
async def mark_not_helpful(callback: CallbackQuery):
    """Mark review as not helpful"""
    review_id = int(callback.data.split("_")[2])
    telegram_id = callback.from_user.id
    lang = db.get_user_language(telegram_id)

    db.increment_review_not_helpful_count(review_id)

    await callback.answer(get_text('marked_not_helpful', lang))


@router.callback_query(F.data.startswith("reviews_page_"))
async def reviews_pagination(callback: CallbackQuery):
    """Navigate review pages"""
    parts = callback.data.split("_")
    apartment_id = int(parts[2])
    page = int(parts[3])
    telegram_id = callback.from_user.id
    lang = db.get_user_language(telegram_id)

    # Validate apartment exists
    apartment = db.get_apartment_by_id(apartment_id)
    if not apartment:
        await callback.answer(get_text('apartment_not_found', lang), show_alert=True)
        return

    offset = (page - 1) * REVIEWS_PER_PAGE
    reviews = db.get_apartment_reviews(apartment_id, limit=REVIEWS_PER_PAGE, offset=offset)

    if reviews:
        text = get_text('reviews_title', lang) + "\n\n"
        for review in reviews:
            stars = "⭐" * review['rating']
            text += f"{stars} {review['rating']}.0\n"
            text += f"👤 {review['user_name']}\n"
            if review.get('comment'):
                text += f"{review['comment']}\n\n"

        with db.get_db() as conn:
            total = conn.execute("SELECT COUNT(*) FROM reviews WHERE apartment_id = ?", (apartment_id,)).fetchone()[0]
        total_pages = (total + REVIEWS_PER_PAGE - 1) // REVIEWS_PER_PAGE

        await callback.message.edit_text(
            text,
            reply_markup=get_reviews_pagination_keyboard(apartment_id, page, total_pages, lang)
        )
    await callback.answer()


@router.callback_query(F.data == "reviews_back")
async def reviews_back(callback: CallbackQuery):
    """Back from reviews"""
    await callback.message.delete()
    await callback.answer()
