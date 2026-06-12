"""
auth_helpers.py
---------------
Decorators and utilities for protecting routes.

Two strategies supported:
  1. Firebase ID Token  (Authorization: Bearer <firebase_id_token>)
  2. Custom JWT         (Authorization: Bearer <jwt>)  — for non-Firebase clients
"""
from functools import wraps
from flask import request, jsonify, g
from firebase_admin import auth as firebase_auth
import jwt as pyjwt
from flask import current_app


# ------------------------------------------------------------------ #
#  Firebase ID-Token verification (primary)                           #
# ------------------------------------------------------------------ #

def verify_firebase_token(id_token: str) -> dict | None:
    try:
        decoded = firebase_auth.verify_id_token(id_token)
        return decoded
    except Exception:
        return None


def firebase_required(f):
    """Verify Firebase ID token; sets g.uid and g.user_claims."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing token"}), 401
        token = auth_header.split("Bearer ")[1]
        claims = verify_firebase_token(token)
        if not claims:
            return jsonify({"error": "Invalid or expired token"}), 401
        g.uid          = claims["uid"]
        g.user_claims  = claims
        return f(*args, **kwargs)
    return decorated


# ------------------------------------------------------------------ #
#  Custom JWT (fallback / testing)                                    #
# ------------------------------------------------------------------ #

def issue_jwt(uid: str, extra: dict = {}) -> str:
    payload = {"sub": uid, **extra}
    return pyjwt.encode(
        payload,
        current_app.config["JWT_SECRET_KEY"],
        algorithm="HS256",
    )


def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing token"}), 401
        token = auth_header.split("Bearer ")[1]
        try:
            payload = pyjwt.decode(
                token,
                current_app.config["JWT_SECRET_KEY"],
                algorithms=["HS256"],
            )
        except pyjwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except pyjwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        g.uid         = payload["sub"]
        g.user_claims = payload
        return f(*args, **kwargs)
    return decorated


# Use whichever strategy your frontend sends
auth_required = firebase_required
