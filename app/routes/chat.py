"""routes/chat.py"""
from flask import Blueprint, request, g
from app.utils.responses import success, error, paginated
from app.utils.auth_helpers import auth_required
from app.services.chat_service import (
    list_conversations, get_messages, send_message, delete_message,
)

chat_bp = Blueprint("chat", __name__)

@chat_bp.get("/conversations")
@auth_required
def route_convos():
    items = list_conversations(g.uid)
    return success(items)

@chat_bp.get("/conversations/<convo_id>/messages")
@auth_required
def route_messages(convo_id):
    page  = int(request.args.get("page", 1))
    size  = int(request.args.get("page_size", 50))
    items, total = get_messages(convo_id, g.uid, page, size)
    return paginated(items, page, size, total)

@chat_bp.post("/conversations/<convo_id>/messages")
@auth_required
def route_send(convo_id):
    body = request.get_json(silent=True) or {}
    if not body.get("text") and not body.get("attachment_url"):
        return error("text or attachment_url required")
    msg = send_message(convo_id, g.uid, body)
    return success(msg, status=201)

@chat_bp.delete("/messages/<msg_id>")
@auth_required
def route_delete_msg(msg_id):
    ok = delete_message(msg_id, g.uid)
    return (success(message="Deleted") if ok else error("Not found or not yours", 403))
