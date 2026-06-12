"""
firebase_client.py
------------------
Singleton wrapper around firebase-admin.
Call `get_db()` anywhere in the app to get a Firestore client.
Call `get_auth()` to get the Firebase Auth client.
Call `get_bucket()` to get the Cloud Storage bucket.
"""
import firebase_admin
from firebase_admin import credentials, firestore, auth, storage
from flask import current_app
import functools

_app: firebase_admin.App | None = None


def _init_firebase():
    global _app
    if _app is not None:
        return _app

    cred_path = current_app.config.get("FIREBASE_CREDENTIALS_PATH", "")
    bucket    = current_app.config.get("FIREBASE_STORAGE_BUCKET", "")

    if cred_path:
        cred  = credentials.Certificate(cred_path)
        _app  = firebase_admin.initialize_app(cred, {"storageBucket": bucket})
    else:
        # Use Application Default Credentials (Cloud Run / GKE)
        _app = firebase_admin.initialize_app(options={"storageBucket": bucket})

    return _app


def get_db() -> firestore.Client:
    _init_firebase()
    return firestore.client()


def get_auth() -> auth.Client:
    _init_firebase()
    return auth


def get_bucket():
    _init_firebase()
    return storage.bucket()


# ---------- helpers ----------

def doc_to_dict(doc) -> dict:
    """Convert a Firestore DocumentSnapshot to a plain dict with 'id' field."""
    if not doc.exists:
        return {}
    d = doc.to_dict()
    d["id"] = doc.id
    return d


def paginate_query(query, page: int, page_size: int):
    """Simple offset-based pagination helper."""
    offset = (page - 1) * page_size
    return query.offset(offset).limit(page_size)
