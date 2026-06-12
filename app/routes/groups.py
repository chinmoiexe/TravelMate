"""routes/groups.py"""
from flask import Blueprint, request, g
from app.utils.responses import success, error, paginated
from app.utils.auth_helpers import auth_required
from app.services.groups_service import (
    list_groups, get_group, create_group, update_group, delete_group,
    toggle_membership, get_members,
)

groups_bp = Blueprint("groups", __name__)

@groups_bp.get("/")
@auth_required
def route_list():
    page     = int(request.args.get("page", 1))
    size     = int(request.args.get("page_size", 20))
    category = request.args.get("category")
    items, total = list_groups(g.uid, page, size, category=category)
    return paginated(items, page, size, total)

@groups_bp.post("/")
@auth_required
def route_create():
    body = request.get_json(silent=True) or {}
    if not body.get("name"):
        return error("name is required")
    group = create_group(g.uid, body)
    return success(group, status=201)

@groups_bp.get("/<group_id>")
@auth_required
def route_get(group_id):
    group = get_group(group_id, viewer_uid=g.uid)
    return (success(group) if group else error("Not found", 404))

@groups_bp.patch("/<group_id>")
@auth_required
def route_update(group_id):
    body = request.get_json(silent=True) or {}
    ok   = update_group(group_id, g.uid, body)
    return (success(message="Updated") if ok else error("Not found or not owner", 403))

@groups_bp.delete("/<group_id>")
@auth_required
def route_delete(group_id):
    ok = delete_group(group_id, g.uid)
    return (success(message="Deleted") if ok else error("Not found or not owner", 403))

@groups_bp.post("/<group_id>/join")
@auth_required
def route_join(group_id):
    status = toggle_membership(group_id, g.uid)
    return success({"status": status})

@groups_bp.get("/<group_id>/members")
@auth_required
def route_members(group_id):
    page  = int(request.args.get("page", 1))
    size  = int(request.args.get("page_size", 50))
    items, total = get_members(group_id, page, size)
    return paginated(items, page, size, total)
