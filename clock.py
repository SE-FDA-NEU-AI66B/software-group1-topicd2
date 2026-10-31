"""Single source of the current time.

Application code calls clock.now() and clock.today() instead of
datetime.now() / date.today(), so tests can freeze time by replacing
clock.now (see tests/conftest.py).
"""

from datetime import date, datetime


def now() -> datetime:
    return datetime.now()


def today() -> date:
    return now().date()
