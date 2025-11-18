"""
Centralized logging configuration for the Telegram bot
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime
import config

# Create logs directory if it doesn't exist
LOGS_DIR = Path(__file__).parent.parent / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# Log file paths
BOT_LOG_FILE = LOGS_DIR / 'bot.log'
ERROR_LOG_FILE = LOGS_DIR / 'error.log'
AUDIT_LOG_FILE = LOGS_DIR / 'audit.log'


def setup_logger(name: str = 'telegram_bot', level: str = None):
    """
    Setup and configure logger with file and console handlers

    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    if level is None:
        level = config.LOG_LEVEL

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level))

    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()

    # Console handler - INFO and above
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)

    # File handler for all logs - rotating 10MB files, keep 5 backups
    file_handler = RotatingFileHandler(
        BOT_LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)

    # Error file handler - ERROR and CRITICAL only
    error_handler = RotatingFileHandler(
        ERROR_LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)

    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)

    return logger


def get_audit_logger():
    """
    Get audit logger for tracking critical operations
    (registrations, bookings, admin actions, etc.)
    """
    audit_logger = logging.getLogger('audit')
    audit_logger.setLevel(logging.INFO)

    # Clear existing handlers
    audit_logger.handlers.clear()

    # Audit file handler - separate file for audit trail
    audit_handler = RotatingFileHandler(
        AUDIT_LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=10,  # Keep more audit logs
        encoding='utf-8'
    )
    audit_handler.setLevel(logging.INFO)
    audit_formatter = logging.Formatter(
        '%(asctime)s - AUDIT - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    audit_handler.setFormatter(audit_formatter)
    audit_logger.addHandler(audit_handler)

    # Don't propagate to root logger to avoid duplication
    audit_logger.propagate = False

    return audit_logger


# Helper functions for structured logging
def log_user_action(logger, user_id: int, action: str, details: str = None):
    """Log user action"""
    msg = f"User {user_id} - {action}"
    if details:
        msg += f" - {details}"
    logger.info(msg)


def log_booking_action(audit_logger, user_id: int, booking_id: int, action: str, details: str = None):
    """Log booking-related action to audit log"""
    msg = f"Booking {booking_id} - User {user_id} - {action}"
    if details:
        msg += f" - {details}"
    audit_logger.info(msg)


def log_error(logger, error: Exception, context: str = None):
    """Log error with context"""
    msg = f"Error"
    if context:
        msg += f" in {context}"
    msg += f": {str(error)}"
    logger.error(msg, exc_info=True)


def log_admin_action(audit_logger, admin_id: int, action: str, target: str = None):
    """Log admin action to audit log"""
    msg = f"Admin {admin_id} - {action}"
    if target:
        msg += f" - Target: {target}"
    audit_logger.info(msg)


# Create default logger instance
default_logger = setup_logger()
audit_logger = get_audit_logger()
