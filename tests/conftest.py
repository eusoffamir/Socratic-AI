import pytest

from app import storage


@pytest.fixture(autouse=True)
def _never_touch_the_real_database(monkeypatch):
    """Tests always save to files, even if .env has Supabase keys."""
    monkeypatch.setattr(storage, "BACKEND", "files")
