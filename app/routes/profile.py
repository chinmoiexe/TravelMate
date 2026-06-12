from flask import Blueprint, request, g
from app.utils.responses import success, error
from app.utils.auth_helpers import auth_required
from app.services.profile_service import (
    get_profile, update_profile, follow_user, unfollow_user,
    get_followers, get_following,
)

profile_bp = Blueprint("profile", __name__)

@profile_bp.get("/<uid>")
@auth_required
def route_profile(uid):
    p = get_profile(uid, viewer_uid=g.uid)
    return (success(p) if p else error("Not found", 404))

@profile_bp.patch("/me")
@auth_required
def route_update():
    body = request.get_json(silent=True) or {}
    updated = update_profile(g.uid, body)
    return success(updated)

@profile_bp.post("/<uid>/follow")
@auth_required
def route_follow(uid):
    if uid == g.uid:
        return error("Cannot follow yourself")
    follow_user(g.uid, uid)
    return success(message="Following")

@profile_bp.delete("/<uid>/follow")
@auth_required
def route_unfollow(uid):
    unfollow_user(g.uid, uid)
    return success(message="Unfollowed")

@profile_bp.get("/<uid>/followers")
@auth_required
def route_followers(uid):
    page = int(request.args.get("page", 1))
    size = int(request.args.get("page_size", 50))
    items, total = get_followers(uid, page, size)
    from app.utils.responses import paginated as pg
    return pg(items, page, size, total)

@profile_bp.get("/<uid>/following")
@auth_required
def route_following(uid):
    page = int(request.args.get("page", 1))
    size = int(request.args.get("page_size", 50))
    items, total = get_following(uid, page, size)
    from app.utils.responses import paginated as pg
    return pg(items, page, size, total)
