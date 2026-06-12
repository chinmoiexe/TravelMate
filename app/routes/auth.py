"""
routes/auth.py
--------------
POST /api/auth/send-otp      — send OTP via Twilio or Firebase Phone Auth
POST /api/auth/verify-otp    — verify OTP, return Firebase custom token
POST /api/auth/refresh        — refresh JWT
POST /api/auth/logout         — invalidate session
GET  /api/auth/me             — return current user profile
"""
from flask import Blueprint, request, g
from app.utils.responses import success, error
from app.utils.auth_helpers import auth_required
from app.services.auth_service import (
    send_otp,
    verify_otp_and_issue_token,
    get_or_create_user,
    revoke_user_tokens,
)

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/send-otp")
def route_send_otp():
    body  = request.get_json(silent=True) or {}
    phone = body.get("phone", "").strip()
    if not phone:
        return error("phone is required")
    result = send_otp(phone)
    if not result["ok"]:
        return error(result["message"], 500)
    return success(message="OTP sent")


@auth_bp.post("/verify-otp")
def route_verify_otp():
    body  = request.get_json(silent=True) or {}
    phone = body.get("phone", "").strip()
    code  = body.get("code", "").strip()
    if not phone or not code:
        return error("phone and code are required")

    result = verify_otp_and_issue_token(phone, code)
    if not result["ok"]:
        return error(result["message"], 401)

    user = get_or_create_user(phone, result["uid"])
    return success({
        "token":         result["token"],
        "refresh_token": result.get("refresh_token"),
        "user":          user,
    })


@auth_bp.get("/me")
@auth_required
def route_me():
    from app.services.profile_service import get_profile
    profile = get_profile(g.uid)
    if not profile:
        return error("User not found", 404)
    return success(profile)


@auth_bp.post("/logout")
@auth_required
def route_logout():
    revoke_user_tokens(g.uid)
    return success(message="Logged out")
