from flask import Blueprint, request, g
from app.utils.responses import success, error, paginated
from app.utils.auth_helpers import auth_required
from app.services.ratings_service import (
    get_ratings, submit_rating, get_summary,
)

ratings_bp = Blueprint("ratings", __name__)

@ratings_bp.get("/user/<uid>")
@auth_required
def route_user_ratings(uid):
    page  = int(request.args.get("page", 1))
    size  = int(request.args.get("page_size", 20))
    items, total = get_ratings("user", uid, page, size)
    return paginated(items, page, size, total)

@ratings_bp.get("/group/<group_id>")
@auth_required
def route_group_ratings(group_id):
    page  = int(request.args.get("page", 1))
    size  = int(request.args.get("page_size", 20))
    items, total = get_ratings("group", group_id, page, size)
    return paginated(items, page, size, total)

@ratings_bp.get("/summary/<entity_type>/<entity_id>")
@auth_required
def route_summary(entity_type, entity_id):
    summary = get_summary(entity_type, entity_id)
    return success(summary)

@ratings_bp.post("/")
@auth_required
def route_submit():
    body = request.get_json(silent=True) or {}
    required = ["entity_type", "entity_id", "score"]
    if missing := [f for f in required if not body.get(f)]:
        return error(f"Missing fields: {', '.join(missing)}")
    rating = submit_rating(g.uid, body)
    return success(rating, status=201)
