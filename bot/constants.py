"""
Application constants and configuration values
Centralized location for all magic numbers and hardcoded values
"""

# Telegram limits
MAX_PHOTOS_PER_MESSAGE = 10  # Telegram limit for media group

# Pagination
REVIEWS_PER_PAGE = 5
BOOKINGS_HISTORY_LIMIT = 10

# Booking constraints
MIN_BOOKING_DAYS = 1

# Review constraints
MIN_RATING = 1
MAX_RATING = 5
MIN_REVIEW_COMMENT_LENGTH = 10
MAX_REVIEW_COMMENT_LENGTH = 1000

# Rate limiting
RATE_LIMIT_REQUESTS = 10
RATE_LIMIT_PERIOD = 60  # seconds
RATE_LIMIT_BURST = 20
RATE_LIMIT_WARNING_COOLDOWN = 300  # 5 minutes
RATE_LIMIT_CLEANUP_INTERVAL = 300  # 5 minutes
RATE_LIMIT_CLEANUP_THRESHOLD_HOURS = 1

# Price formatting
PRICE_THOUSANDS_SEPARATOR = ' '
PRICE_CURRENCY = '₸'
