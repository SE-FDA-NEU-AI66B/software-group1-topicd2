# Task #94: Import the Admin API blueprint for application-level registration.
from .admin import admin_api_bp
from .auth import auth_bp
from .bank_accounts import bank_accounts_bp
from .bookings import bookings_bp
from .pages import pages_bp

# Task #94: Export the Admin API blueprint so the application can register it.
__all__ = ("admin_api_bp", "auth_bp", "bank_accounts_bp", "bookings_bp", "pages_bp")
