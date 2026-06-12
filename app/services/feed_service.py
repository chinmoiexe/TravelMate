from app.utils.firebase_client import get_db, doc_to_dict, paginate_query
from datetime import datetime, timezone

def _now(): return datetime.now(timezone.utc).isoformat()
def _increment(n):
    from google.cloud.firestore import Increment
    return Increment(n)

def get_feed(uid, page, page_size, category=None):
    db = get_db()
    q = db.collection("posts").order_by("created_at", direction="DESCENDING")
    if category and category.lower() != "all":
        q = q.where("category", "==", category)
    return [doc_to_dict(d) for d in paginate_query(q, page, page_size).stream()], 0

def get_stories(uid):
    db = get_db()
    docs = db.collection("stories").where("expires_at", ">", _now()).limit(30).stream()
    return [doc_to_dict(d) for d in docs]

def create_post(uid, body):
    db = get_db(); ref = db.collection("posts").document()
    post = {"id": ref.id, "uid": uid, "caption": body.get("caption",""), "location": body.get("location",""), "category": body.get("category",""), "media_urls": body.get("media_urls",[]), "tags": body.get("tags",[]), "likes": 0, "saves": 0, "comments": 0, "created_at": _now()}
    ref.set(post); return post

def get_post(post_id, viewer_uid=None):
    doc = get_db().collection("posts").document(post_id).get()
    return doc_to_dict(doc) or None

def delete_post(post_id, uid):
    db = get_db(); doc = db.collection("posts").document(post_id).get()
    if not doc.exists or doc.to_dict().get("uid") != uid: return False
    db.collection("posts").document(post_id).delete(); return True

def toggle_like(post_id, uid):
    db = get_db(); ref = db.collection("posts").document(post_id)
    lr = db.collection("post_likes").document(f"{post_id}_{uid}")
    if lr.get().exists:
        lr.delete(); ref.update({"likes": _increment(-1)}); liked = False
    else:
        lr.set({"post_id": post_id, "uid": uid, "created_at": _now()}); ref.update({"likes": _increment(1)}); liked = True
    return liked, ref.get().to_dict().get("likes", 0)

def toggle_save(post_id, uid):
    db = get_db(); sr = db.collection("post_saves").document(f"{post_id}_{uid}")
    if sr.get().exists: sr.delete(); return False
    sr.set({"post_id": post_id, "uid": uid, "created_at": _now()}); return True

def get_trending():
    db = get_db()
    return [doc_to_dict(d) for d in db.collection("trending_destinations").order_by("growth_pct", direction="DESCENDING").limit(10).stream()]

def get_suggestions(uid):
    db = get_db()
    return [doc_to_dict(d) for d in db.collection("users").where("uid","!=",uid).order_by("uid").limit(10).stream()]
