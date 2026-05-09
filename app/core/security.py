import hashlib
import hmac
import secrets
import base64
import json
import time
from app.core.config import get_settings

settings = get_settings()
SECRET = settings.APP_SECRET_KEY.encode()
JWT_EXPIRE_SECONDS = 60 * 60 * 24 * 7  # 7 days


# ── Password hashing (PBKDF2 — no extra libs needed) ─────────────────────────

def hash_password(plain: str) -> str:
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac("sha256", plain.encode(), salt.encode(), 260_000)
    return f"{salt}:{key.hex()}"


def verify_password(plain: str, hashed: str) -> bool:
    try:
        salt, stored_key = hashed.split(":")
        key = hashlib.pbkdf2_hmac("sha256", plain.encode(), salt.encode(), 260_000)
        return hmac.compare_digest(key.hex(), stored_key)
    except Exception:
        return False


# ── Lightweight JWT (HS256) ───────────────────────────────────────────────────
# Using stdlib only — no python-jose needed

def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64url_decode(s: str) -> bytes:
    padding = 4 - len(s) % 4
    return base64.urlsafe_b64decode(s + "=" * padding)


def create_access_token(user_id: int, email: str) -> str:
    header = _b64url_encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    payload = _b64url_encode(json.dumps({
        "sub": str(user_id),
        "email": email,
        "exp": int(time.time()) + JWT_EXPIRE_SECONDS,
    }).encode())
    sig_input = f"{header}.{payload}".encode()
    sig = hmac.new(SECRET, sig_input, hashlib.sha256).digest()
    return f"{header}.{payload}.{_b64url_encode(sig)}"


def decode_access_token(token: str) -> dict:
    try:
        header, payload, sig = token.split(".")
        sig_input = f"{header}.{payload}".encode()
        expected_sig = hmac.new(SECRET, sig_input, hashlib.sha256).digest()
        if not hmac.compare_digest(_b64url_decode(sig), expected_sig):
            raise ValueError("Invalid signature")
        data = json.loads(_b64url_decode(payload))
        if data.get("exp", 0) < int(time.time()):
            raise ValueError("Token expired")
        return data
    except ValueError:
        raise
    except Exception:
        raise ValueError("Malformed token")
