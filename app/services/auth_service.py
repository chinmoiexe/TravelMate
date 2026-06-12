"""
services/auth_service.py
------------------------
Handles OTP sending and verification.

Strategy:
  - Primary:  Firebase Phone Authentication (handles OTP natively on mobile)
  - Fallback: Twilio Verify for web or custom flows
"""
import os
import random
import string
import time
from flask import current_app
from app.utils.firebase_client import get_db, get_auth, doc_to_dict

# In-memory OTP store for demo/testing — replace with Redis in production
_otp_store: dict[str, dict] = {}


# ------------------------------------------------------------------ #
#  OTP Send                                                           #
# ------------------------------------------------------------------ #

def send_otp(phone: str) -> dict:
    """
    Send a 6-digit OTP to `phone`.
    Uses Twilio Verify if credentials are configured, otherwise logs to console.
    """
    code = _generate_code()
    _otp_store[phone] = {"code": code, "expires": time.time() + 600}  # 10 min

    sid   = current_app.config.get("TWILIO_ACCOUNT_SID")
    token = current_app.config.get("TWILIO_AUTH_TOKEN")
    svc   = os.getenv("TWILIO_VERIFY_SERVICE_SID", "")

    if sid and token and svc:
        try:
            from twilio.rest import Client
            client = Client(sid, token)
            client.verify.v2.services(svc).verifications.create(
                to=phone, channel="sms"
            )
            return {"ok": True}
        except Exception as e:
            current_app.logger.error(f"Twilio error: {e}")
            # Fall through to console fallback

    # Dev fallback — print code to server logs
    current_app.logger.info(f"[DEV OTP] {phone} → {code}")
    return {"ok": True}


# ------------------------------------------------------------------ #
#  OTP Verify                                                         #
# ------------------------------------------------------------------ #

def verify_otp_and_issue_token(phone: str, code: str) -> dict:
    """Verify the OTP and return a Firebase custom token."""
    entry = _otp_store.get(phone)
    if not entry:
        return {"ok": False, "message": "No OTP found for this number"}
    if time.time() > entry["expires"]:
        _otp_store.pop(phone, None)
        return {"ok": False, "message": "OTP expired"}
    if entry["code"] != code:
        return {"ok": False, "message": "Invalid code"}

    _otp_store.pop(phone, None)

    # Derive a stable UID from the phone number
    uid = _phone_to_uid(phone)
    try:
        firebase_token = get_auth().create_custom_token(uid).decode()
    except Exception as e:
        current_app.logger.error(f"Firebase custom token error: {e}")
        from app.utils.auth_helpers import issue_jwt
        firebase_token = issue_jwt(uid)

    return {"ok": True, "uid": uid, "token": firebase_token}


# ------------------------------------------------------------------ #
#  User bootstrap                                                     #
# ------------------------------------------------------------------ #

def get_or_create_user(phone: str, uid: str) -> dict:
    db   = get_db()
    ref  = db.collection("users").document(uid)
    snap = ref.get()
    if snap.exists:
        return doc_to_dict(snap)

    user = {
        "uid":        uid,
        "phone":      phone,
        "username":   "",
        "display_name": "",
        "avatar_url": "",
        "bio":        "",
        "tags":       [],
        "countries":  [],
        "followers":  0,
        "following":  0,
        "posts":      0,
        "created_at": _now(),
        "online":     True,
    }
    ref.set(user)
    return user


def revoke_user_tokens(uid: str):
    try:
        get_auth().revoke_refresh_tokens(uid)
    except Exception as e:
        current_app.logger.warning(f"Token revocation failed for {uid}: {e}")


# ------------------------------------------------------------------ #
#  Helpers                                                            #
# ------------------------------------------------------------------ #

def _generate_code(length=6) -> str:
    return "".join(random.choices(string.digits, k=length))


def _phone_to_uid(phone: str) -> str:
    """Deterministic UID from phone (strips non-digits)."""
    digits = "".join(c for c in phone if c.isdigit())
    return f"phone_{digits}"


def _now():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()
