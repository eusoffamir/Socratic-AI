"""A daily budget of AI calls, so the free Gemini quota is never used up
before the day ends. Plain code, no AI.

Gemini's free tier for gemini-3.5-flash-lite allows 500 calls a day (seen in
Google AI Studio, 15 October 2026). One 6-round session uses about 30 to 35.
New sessions stop at DAILY_CALL_BUDGET, so the calls left over let sessions
that already started finish. Sessions already running are never blocked.

Why no limit per visitor: in a class, every student comes from the same
university network, so a limit per address would block the whole class.

Set DAILY_CALL_BUDGET in .env or on Render (0 = no limit), for example higher
if the project gets a paid key. The count lives in memory, so it restarts at 0
when Render restarts the app. It is a guard, not an exact meter: Gemini still
enforces its own limit.
"""
import os
import threading
from datetime import datetime, timedelta, timezone

DAILY_CALL_BUDGET = int(os.getenv("DAILY_CALL_BUDGET", "400"))

# Google resets the daily count at midnight US Pacific time. UTC-8 is close
# enough (an hour off in summer), and needs no time zone files on Windows.
_PACIFIC = timezone(timedelta(hours=-8))

FULL_MESSAGE = "The app has reached its daily limit, so please try again tomorrow."

_lock = threading.Lock()
_day, _calls = None, 0


def _today():
    return datetime.now(_PACIFIC).date()


def count_call():
    """Called once for every real model call."""
    global _day, _calls
    with _lock:
        if _day != _today():
            _day, _calls = _today(), 0
        _calls += 1


def calls_today():
    with _lock:
        return _calls if _day == _today() else 0


def budget_left():
    """True while new sessions may start."""
    return DAILY_CALL_BUDGET <= 0 or calls_today() < DAILY_CALL_BUDGET
