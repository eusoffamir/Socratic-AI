"""Load settings from .env safely when .env is encrypted with dotenvx.

The .env file in the repo is encrypted with dotenvx, so it can be shared
through GitHub across devices. Each value looks like "encrypted:...".

- `dotenvx run -- <command>` decrypts it and puts the real values in the
  environment before Python starts, so nothing here needs to change them.
- Without dotenvx (for example on Render, which keeps its own values in the
  dashboard), the encrypted values are skipped, so they never replace a real
  setting or a default with scrambled text.
"""

import os
from pathlib import Path

from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parent.parent
ENCRYPTED_PREFIX = "encrypted:"


def load_env(path: Path | None = None) -> None:
    """Copy plain values from .env into os.environ, never overriding what is set."""
    # If `dotenvx run` could not decrypt (wrong or missing DOTENV_PRIVATE_KEY),
    # it still passes the scrambled "encrypted:..." text on. Drop it, so the
    # app falls back to its defaults (mock mode) instead of crashing.
    failed = [k for k, v in os.environ.items() if v.startswith(ENCRYPTED_PREFIX)]
    for key in failed:
        del os.environ[key]
    if failed:
        print(
            f"[env] Could not decrypt {len(failed)} value(s) from .env, so they "
            "were ignored and the app uses its defaults. Check that "
            "DOTENV_PRIVATE_KEY is set and matches the key on your other devices."
        )

    env_file = path or ROOT / ".env"
    if not env_file.exists():
        return
    skipped = 0
    for key, value in dotenv_values(env_file).items():
        if key in os.environ or value is None:
            continue
        if value.startswith(ENCRYPTED_PREFIX):
            skipped += 1
            continue
        os.environ[key] = value
    if skipped and not os.environ.get("RENDER"):
        print(
            f"[env] Skipped {skipped} encrypted value(s) in .env. "
            "Run with `dotenvx run -- <command>` to use them."
        )
