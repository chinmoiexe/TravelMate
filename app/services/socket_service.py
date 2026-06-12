"""
services/socket_service.py
--------------------------
All Socket.IO event handlers live here.

Events emitted BY server:
  new_message        → { convo_id, message }
  typing             → { convo_id, uid, is_typing }
  presence_update    → { uid, online, last_seen }
  tracking_update    → { journey_id, progress, status, coords }
  notification       → { type, payload }

Events received FROM client:
  join_conversation  → { convo_id }
  leave_conversation → { convo_id }
  send_message       → { convo_id, text, attachment_url? }
  typing_start       → { convo_id }
  typing_stop        → { convo_id }
  update_presence    → { online: bool }
"""
from app import socketio
from flask import request
from flask_socketio import join_room, leave_room, emit
from app.utils.firebase_client import get_db
from datetime import datetime, timezone


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


# ------------------------------------------------------------------ #
#  Connection lifecycle                                               #
# ------------------------------------------------------------------ #

@socketio.on("connect")
def on_connect():
    uid = request.args.get("uid")
    if not uid:
        return False  # reject unauthenticated connections
    join_room(f"user:{uid}")
    _set_presence(uid, online=True)
    emit("connected", {"uid": uid, "ts": _now_iso()})


@socketio.on("disconnect")
def on_disconnect():
    uid = request.args.get("uid")
    if uid:
        _set_presence(uid, online=False)


# ------------------------------------------------------------------ #
#  Chat                                                               #
# ------------------------------------------------------------------ #

@socketio.on("join_conversation")
def on_join(data):
    convo_id = data.get("convo_id")
    uid      = request.args.get("uid")
    if convo_id and uid:
        join_room(f"convo:{convo_id}")


@socketio.on("leave_conversation")
def on_leave(data):
    convo_id = data.get("convo_id")
    if convo_id:
        leave_room(f"convo:{convo_id}")


@socketio.on("send_message")
def on_message(data):
    convo_id = data.get("convo_id")
    uid      = request.args.get("uid")
    text     = data.get("text", "").strip()
    if not convo_id or not uid or not text:
        return

    msg = {
        "id":         _generate_id(),
        "convo_id":   convo_id,
        "sender_uid": uid,
        "text":       text,
        "attachment_url": data.get("attachment_url"),
        "created_at": _now_iso(),
        "read_by":    [uid],
    }

    # Persist to Firestore
    try:
        db = get_db()
        db.collection("messages").document(msg["id"]).set(msg)
        db.collection("conversations").document(convo_id).update({
            "last_message": text,
            "last_message_at": msg["created_at"],
            f"unread.{uid}": 0,  # reset sender's unread
        })
    except Exception:
        pass  # degrade gracefully; message still broadcasts

    # Broadcast to room
    emit("new_message", {"convo_id": convo_id, "message": msg},
         room=f"convo:{convo_id}", include_self=True)


@socketio.on("typing_start")
def on_typing_start(data):
    convo_id = data.get("convo_id")
    uid      = request.args.get("uid")
    if convo_id and uid:
        emit("typing", {"convo_id": convo_id, "uid": uid, "is_typing": True},
             room=f"convo:{convo_id}", include_self=False)


@socketio.on("typing_stop")
def on_typing_stop(data):
    convo_id = data.get("convo_id")
    uid      = request.args.get("uid")
    if convo_id and uid:
        emit("typing", {"convo_id": convo_id, "uid": uid, "is_typing": False},
             room=f"convo:{convo_id}", include_self=False)


# ------------------------------------------------------------------ #
#  Presence                                                           #
# ------------------------------------------------------------------ #

@socketio.on("update_presence")
def on_presence(data):
    uid    = request.args.get("uid")
    online = data.get("online", True)
    if uid:
        _set_presence(uid, online)


def _set_presence(uid: str, online: bool):
    payload = {"uid": uid, "online": online, "last_seen": _now_iso()}
    try:
        get_db().collection("users").document(uid).update(payload)
    except Exception:
        pass
    # Broadcast to all followers (simplified: broadcast globally)
    socketio.emit("presence_update", payload)


# ------------------------------------------------------------------ #
#  Server-side helpers for pushing tracking updates                  #
# ------------------------------------------------------------------ #

def push_tracking_update(uid: str, journey_id: str, update: dict):
    """Called by a background job when a flight/train status changes."""
    socketio.emit(
        "tracking_update",
        {"journey_id": journey_id, **update},
        room=f"user:{uid}",
    )


def push_notification(uid: str, notif_type: str, payload: dict):
    """Push a notification to a specific user."""
    socketio.emit(
        "notification",
        {"type": notif_type, "payload": payload, "ts": _now_iso()},
        room=f"user:{uid}",
    )


# ------------------------------------------------------------------ #
#  Utils                                                              #
# ------------------------------------------------------------------ #

def _generate_id(length=20) -> str:
    import random, string
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))
