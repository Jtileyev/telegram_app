"""
Reviews handlers - review management
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
from keyboards import get_reviews_pagination_keyboard
from locales import get_text
from constants import REVIEWS_PER_PAGE

router = Router()


class ReviewStates(StatesGroup):
    selecting_rating = State()
    writing_comment = State()


@router.callback_query(F.data.startswith("reviews_"))
async def show_reviews(callback: CallbackQuery, state: FSMContext):
    """Show apartment reviews"""
    if callback.data.startswith("reviews_page_"):
        return  # Handled by reviews_pagination

    apartment_id = int(callback.data.split("_")[1])
    telegram_id = callback.from_user.id
    lang = db.get_user_language(telegram_id)

    reviews = db.get_apartment_reviews(apartment_id, limit=REVIEWS_PER_PAGE)

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


@router.callback_query(F.data.startswith("rating_"))
async def select_rating(callback: CallbackQuery, state: FSMContext):
    """Select review rating"""
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

    await state.update_data(rating=rating)
    await callback.message.edit_text(get_text('rating_selected', lang, rating=rating))
    await callback.message.answer(get_text('enter_review_comment', lang))
    await state.set_state(ReviewStates.writing_comment)
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

        conn = db.get_connection()
        total = conn.execute("SELECT COUNT(*) FROM reviews WHERE apartment_id = ?", (apartment_id,)).fetchone()[0]
        conn.close()
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
