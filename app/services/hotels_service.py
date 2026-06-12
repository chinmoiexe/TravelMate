# hotels_service.py — implement Firestore logic here
from app.utils.firebase_client import get_db, doc_to_dict, paginate_query
from datetime import datetime, timezone

def _now(): return datetime.now(timezone.utc).isoformat()
def _increment(n):
    from google.cloud.firestore import Increment
    return Increment(n)
