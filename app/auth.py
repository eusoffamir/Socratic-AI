"""Optional sign-in with Google, so a learner's chats, topics and mastery follow
them to any device. Guests still work as before (everything kept in the browser).

How it works:
  1. The page shows Google's own "Sign in with Google" button (only when
     GOOGLE_CLIENT_ID is set). Google gives the page a signed ID token.
  2. The server asks Google to check that token (the tokeninfo address), so no
     extra library is needed, and makes sure it was made for this app.
  3. The server gives the browser its own signed cookie, which lasts 90 days.

No names or emails are saved. The profile is stored under a one-way hash of the
Google account id, and the first name and picture live only inside the cookie,
so the "no personal data stored" promise in main.py still holds.
"""
import base64
import hashlib
import hmac
import json
import logging
import os
import secrets
import time

import httpx

COOKIE = "sai_auth"
MAX_AGE = 90 * 24 * 3600  # seconds the sign-in lasts
TOKENINFO = "https://oauth2.googleapis.com/tokeninfo"
ISSUERS = {"accounts.google.com", "https://accounts.google.com"}

# What the page keeps per learner. Each is a list or a small map of ids, plus the
# built topics, so the whole profile stays well under the size limit below.
SYNCED = ("ask-chats", "my-topics", "my-sessions", "my-checks", "saved-sessions")
MAX_PROFILE_BYTES = 400_000

log = logging.getLogger("socratic.auth")

# AUTH_SECRET signs the cookie. Without it a random one is made at start, which
# works but signs everyone out on every restart, so set it on Render.
_SECRET = os.getenv("AUTH_SECRET", "").strip() or secrets.token_hex(32)
if not os.getenv("AUTH_SECRET", "").strip():
    log.warning("AUTH_SECRET is not set, so sign-ins end when the server restarts.")


def client_id():
    """Read each time, so tests can switch it. Empty means sign-in is off."""
    return os.getenv("GOOGLE_CLIENT_ID", "").strip()


class AuthError(Exception):
    pass


def _tokeninfo(credential):
    r = httpx.get(TOKENINFO, params={"id_token": credential}, timeout=10)
    if r.status_code != 200:
        raise AuthError("Google did not accept this sign-in.")
    return r.json()


def verify_google(credential):
    """The checked claims of a Google ID token, or AuthError."""
    if not client_id():
        raise AuthError("Sign-in is not set up on this server.")
    if not credential or len(credential) > 4096:
        raise AuthError("The sign-in was empty or too long.")
    try:
        claims = _tokeninfo(credential)
    except httpx.HTTPError:
        raise AuthError("Google could not be reached, so please try again.")
    if claims.get("aud") != client_id() or claims.get("iss") not in ISSUERS:
        raise AuthError("This sign-in was not made for this app.")
    if int(claims.get("exp", 0)) < time.time() or not claims.get("sub"):
        raise AuthError("This sign-in has expired, so please try again.")
    return claims


def user_id(sub):
    """A one-way hash of the Google account id, used as the profile's key."""
    return hashlib.sha256(f"socratic-ai:{sub}".encode()).hexdigest()


def _b64(b):
    return base64.urlsafe_b64encode(b).decode().rstrip("=")


def _unb64(s):
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def _sign(body):
    return _b64(hmac.new(_SECRET.encode(), body.encode(), hashlib.sha256).digest())


def make_cookie(claims, now=None):
    """The signed cookie value: who this is (hashed), their first name and picture."""
    body = _b64(json.dumps({"uid": user_id(claims["sub"]), "name": (claims.get("given_name") or claims.get("name") or "")[:40],
                            "picture": claims.get("picture", "")[:300],
                            "exp": int(now or time.time()) + MAX_AGE}, separators=(",", ":")).encode())
    return f"{body}.{_sign(body)}"


def read_cookie(value, now=None):
    """The cookie's user {uid, name, picture}, or None when missing, changed or expired."""
    try:
        body, sig = (value or "").split(".")
        if not hmac.compare_digest(sig, _sign(body)):
            return None
        user = json.loads(_unb64(body))
    except (ValueError, json.JSONDecodeError):
        return None
    if user.get("exp", 0) < (now or time.time()) or not user.get("uid"):
        return None
    return user


def clean_profile(data):
    """Only the known keys, each a list or map, and not too big. Raises ValueError."""
    if not isinstance(data, dict):
        raise ValueError("The profile must be an object.")
    out = {k: data[k] for k in SYNCED if isinstance(data.get(k), (list, dict))}
    if len(json.dumps(out)) > MAX_PROFILE_BYTES:
        raise ValueError("The profile is too big.")
    return out
