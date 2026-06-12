"""
routes/feed.py
--------------
GET  /api/feed/                  — paginated home feed
GET  /api/feed/stories           — active stories for current user's network
POST /api/feed/posts             — create a new post
GET  /api/feed/posts/<id>        — single post
DELETE /api/feed/posts/<id>      — delete own post
POST /api/feed/posts/<id>/like   — toggle like
POST /api/feed/posts/<id>/save   — toggle bookmark
GET  /api/feed/trending          — trending destinations
GET  /api/feed/suggestions       — traveler suggestions
"""
from flask import Blueprint, request, g
from app.utils.responses import success, error, paginated
from app.utils.auth_helpers import auth_required
from app.services.feed_service import (
    get_feed,
    get_stories,
    create_post,
    get_post,
    delete_post,
    toggle_like,
    toggle_save,
    get_trending,
    get_suggestions,
)

feed_bp = Blueprint("feed", __name__)


@feed_bp.get("/")
@auth_required
def route_feed():
    page      = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 20))
    category  = request.args.get("category")
    items, total = get_feed(g.uid, page, page_size, category=category)
    return paginated(items, page, page_size, total)


@feed_bp.get("/stories")
@auth_required
def route_stories():
    stories = get_stories(g.uid)
    return success(stories)


@feed_bp.post("/posts")
@auth_required
def route_create_post():
    body = request.get_json(silent=True) or {}
    required = ["caption", "location"]
    if missing := [f for f in required if not body.get(f)]:
        return error(f"Missing fields: {', '.join(missing)}")
    post = create_post(g.uid, body)
    return success(post, status=201)


@feed_bp.get("/posts/<post_id>")
@auth_required
def route_get_post(post_id):
    post = get_post(post_id, viewer_uid=g.uid)
    if not post:
        return error("Post not found", 404)
    return success(post)


@feed_bp.delete("/posts/<post_id>")
@auth_required
def route_delete_post(post_id):
    ok = delete_post(post_id, uid=g.uid)
    if not ok:
        return error("Post not found or not yours", 403)
    return success(message="Post deleted")


@feed_bp.post("/posts/<post_id>/like")
@auth_required
def route_like(post_id):
    liked, count = toggle_like(post_id, g.uid)
    return success({"liked": liked, "count": count})


@feed_bp.post("/posts/<post_id>/save")
@auth_required
def route_save(post_id):
    saved = toggle_save(post_id, g.uid)
    return success({"saved": saved})


@feed_bp.get("/trending")
@auth_required
def route_trending():
    return success(get_trending())


@feed_bp.get("/suggestions")
@auth_required
def route_suggestions():
    return success(get_suggestions(g.uid))
