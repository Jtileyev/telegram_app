"""
Handlers package - contains all message and callback handlers
Split by functionality for better maintainability
"""
from .registration import router as registration_router
from .search import router as search_router
from .booking import router as booking_router
from .reviews import router as reviews_router
from .favorites import router as favorites_router
from .landlords import router as landlords_router

__all__ = [
    'registration_router',
    'search_router',
    'booking_router',
    'reviews_router',
    'favorites_router',
    'landlords_router',
]
