# Bot configuration
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Add parent directory to path to import database module
sys.path.insert(0, str(Path(__file__).parent))
import database as db

def get_bot_token():
    """
    Get bot token from environment variable first, fallback to database
    Environment variables have priority for security
    """
    # Try to get from environment variable first (recommended)
    token = os.getenv('BOT_TOKEN')

    # Fallback to database for backward compatibility
    if not token:
        token = db.get_setting('bot_token')

    if not token:
        raise ValueError(
            "BOT_TOKEN not found! Please set it in .env file or database settings.\n"
            "1. Copy .env.example to .env\n"
            "2. Set BOT_TOKEN=your_token_here in .env file"
        )

    return token

# Database path - from env or default
DATABASE_PATH = os.getenv('DATABASE_PATH',
                         os.path.join(os.path.dirname(__file__), '..', 'database', 'rental.db'))

# Uploads directory - from env or default
UPLOADS_DIR = os.getenv('UPLOADS_DIR',
                       os.path.join(os.path.dirname(__file__), '..', 'uploads'))

# Platform settings - from env or default
PLATFORM_FEE_PERCENT = float(os.getenv('PLATFORM_FEE_PERCENT', '5.0'))

# Reminder settings - from env or defaults
REMINDER_HOURS_BEFORE_CHECKIN = int(os.getenv('REMINDER_HOURS_BEFORE_CHECKIN', '24'))
REMINDER_HOURS_AFTER_CHECKOUT = 48

# Review settings - from env or defaults
MIN_REVIEW_LENGTH = int(os.getenv('MIN_REVIEW_LENGTH', '10'))
MAX_REVIEW_LENGTH = int(os.getenv('MAX_REVIEW_LENGTH', '500'))
REVIEW_EDIT_DAYS = 7

# Environment
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

# Logging level
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
