"""The shared .env must stay encrypted, and the loader must skip encrypted values."""

import os
import subprocess
from pathlib import Path

from dotenv import dotenv_values

from app.env import ENCRYPTED_PREFIX, ROOT, load_env

# Lines dotenvx adds itself; they are public by design.
PUBLIC_KEYS = {"DOTENV_PUBLIC_KEY"}


def _env_is_tracked() -> bool:
    try:
        out = subprocess.run(
            ["git", "ls-files", "--error-unmatch", ".env"],
            cwd=ROOT, capture_output=True, text=True,
        )
    except FileNotFoundError:
        return False
    return out.returncode == 0


def test_tracked_env_has_no_plain_values():
    """If .env is in git (public repo), every filled value must be encrypted."""
    if not _env_is_tracked():
        return
    plain = [
        key for key, value in dotenv_values(ROOT / ".env").items()
        if value and key not in PUBLIC_KEYS and not value.startswith(ENCRYPTED_PREFIX)
    ]
    assert not plain, (
        f"Plain values in the shared .env: {plain}. "
        "Run `dotenvx encrypt` before committing."
    )


def test_load_env_skips_encrypted_and_keeps_existing(tmp_path: Path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "PLAIN_ONE=hello\n"
        "SECRET_ONE=encrypted:abc123\n"
        "ALREADY_SET=from_file\n"
    )
    for key in ("PLAIN_ONE", "SECRET_ONE"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("ALREADY_SET", "from_environment")

    load_env(env_file)

    assert os.environ["PLAIN_ONE"] == "hello"
    assert "SECRET_ONE" not in os.environ
    assert os.environ["ALREADY_SET"] == "from_environment"
    monkeypatch.delenv("PLAIN_ONE", raising=False)


def test_load_env_drops_values_dotenvx_could_not_decrypt(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("PROVIDER", "encrypted:garbled")
    load_env(tmp_path / "missing.env")
    assert "PROVIDER" not in os.environ
