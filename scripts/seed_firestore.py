#!/usr/bin/env python3
"""
scripts/seed_firestore.py
-------------------------
Seed Firestore with demo data for development.

Usage:
    export FIREBASE_CREDENTIALS_PATH=config/firebase-service-account.json
    python scripts/seed_firestore.py
"""
import os, sys, json
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

os.environ.setdefault("FLASK_ENV", "development")
from app import create_app

app = create_app("development")

with app.app_context():
    from app.utils.firebase_client import get_db
    db = get_db()

    def now(offset_hours=0):
        return (datetime.now(timezone.utc) + timedelta(hours=offset_hours)).isoformat()

    print("🌱 Seeding TravelMate Firestore…")

    # ── Trending Destinations ────────────────────────────────────────
    destinations = [
        {"id": "kyoto",      "name": "Kyoto",       "country": "Japan",  "region": "Asia",          "emoji": "🇯🇵", "growth_pct": 128, "category": "Culture",   "updated_at": now()},
        {"id": "patagonia",  "name": "Patagonia",    "country": "Chile",  "region": "South America", "emoji": "🇨🇱", "growth_pct": 94,  "category": "Adventure", "updated_at": now()},
        {"id": "maldives",   "name": "Baa Atoll",    "country": "Maldives","region": "Indian Ocean",  "emoji": "🇲🇻", "growth_pct": 76,  "category": "Diving",    "updated_at": now()},
        {"id": "iceland",    "name": "Reykjavík",    "country": "Iceland","region": "Europe",         "emoji": "🇮🇸", "growth_pct": 61,  "category": "Nature",    "updated_at": now()},
        {"id": "peru",       "name": "Machu Picchu", "country": "Peru",   "region": "South America", "emoji": "🇵🇪", "growth_pct": 55,  "category": "Heritage",  "updated_at": now()},
    ]
    for d in destinations:
        db.collection("trending_destinations").document(d["id"]).set(d)
    print(f"  ✓ {len(destinations)} trending destinations")

    # ── Demo Users ───────────────────────────────────────────────────
    users = [
        {"uid": "user_aria",   "phone": "+15550001", "username": "aria_chen",    "display_name": "Aria Chen",       "avatar_url": "", "bio": "Ocean lover. Maldives addict 🤿",  "tags": ["Diving","Beaches","Photography"], "followers": 4821, "following": 312, "posts": 89,  "countries": ["MV","TH","AU","PH"], "online": True,  "created_at": now()},
        {"uid": "user_marco",  "phone": "+15550002", "username": "marco_v",      "display_name": "Marco Villarreal","avatar_url": "", "bio": "Trekking every continent 🏔️",       "tags": ["Mountains","Trekking","Camping"], "followers": 9204, "following": 891, "posts": 214, "countries": ["CL","AR","PE","NP"], "online": False, "created_at": now()},
        {"uid": "user_yuki",   "phone": "+15550003", "username": "yuki_tanaka",  "display_name": "Yuki Tanaka",     "avatar_url": "", "bio": "Food & shrines. Kyoto forever 🌸", "tags": ["Food","Culture","Japan"],        "followers": 12049,"following": 203, "posts": 341, "countries": ["JP","KR","TW","VN"], "online": True,  "created_at": now()},
        {"uid": "user_alex",   "phone": "+15550004", "username": "alex_jordan",  "display_name": "Alex Jordan",     "avatar_url": "", "bio": "Digital nomad. 47 countries 🌍",   "tags": ["Mountains","Diving","Food"],     "followers": 18400,"following": 892, "posts": 284, "countries": ["JP","CL","MV","IS"], "online": True,  "created_at": now()},
    ]
    for u in users:
        db.collection("users").document(u["uid"]).set(u)
    print(f"  ✓ {len(users)} users")

    # ── Groups ───────────────────────────────────────────────────────
    groups = [
        {"id": "grp_himalaya", "owner_uid": "user_marco",  "name": "Himalayan Trekkers",    "description": "Planning the Annapurna Circuit this October.", "category": "Adventure", "is_private": False, "member_count": 1248, "created_at": now()},
        {"id": "grp_food",     "owner_uid": "user_yuki",   "name": "Street Food Nomads",    "description": "We eat our way around the world.",             "category": "Food",      "is_private": False, "member_count": 3841, "created_at": now()},
        {"id": "grp_photo",    "owner_uid": "user_aria",   "name": "Golden Hour Collective","description": "Invite-only photography trips.",               "category": "Photography","is_private": True,  "member_count": 128,  "created_at": now()},
        {"id": "grp_budget",   "owner_uid": "user_alex",   "name": "Budget Backpackers Asia","description": "Travel SE Asia under $40/day.",              "category": "Backpacking","is_private": False, "member_count": 7302, "created_at": now()},
    ]
    for g in groups:
        db.collection("groups").document(g["id"]).set(g)
    print(f"  ✓ {len(groups)} groups")

    # ── Posts ────────────────────────────────────────────────────────
    posts = [
        {"id": "post_1", "uid": "user_aria",  "caption": "Crystal waters of Baa Atoll 🐠 The snorkeling here is otherworldly.", "location": "Maldives, Baa Atoll",  "category": "Beaches",    "media_urls": [], "tags": ["Maldives","Snorkeling"], "likes": 1284, "saves": 203, "comments": 89,  "created_at": now(-2)},
        {"id": "post_2", "uid": "user_marco", "caption": "Day 4 on the W Trek ⛰️ Legs screaming, soul singing.",               "location": "Patagonia, Chile",     "category": "Mountains",  "media_urls": [], "tags": ["Patagonia","Trekking"],  "likes": 3019, "saves": 541, "comments": 213, "created_at": now(-5)},
        {"id": "post_3", "uid": "user_yuki",  "caption": "Fushimi Inari at dawn 🌅 Got there at 5:30am — completely alone.",   "location": "Kyoto, Japan",         "category": "Culture",    "media_urls": [], "tags": ["Kyoto","Japan"],         "likes": 5421, "saves": 892, "comments": 341, "created_at": now(-8)},
    ]
    for p in posts:
        db.collection("posts").document(p["id"]).set(p)
    print(f"  ✓ {len(posts)} posts")

    # ── Hotels ───────────────────────────────────────────────────────
    hotels = [
        {"id": "hotel_ritz",    "name": "The Ritz-Carlton Kyoto", "city": "Kyoto",    "country": "Japan", "address": "Nakagyo Ward, Kyoto", "lat": 35.0116, "lng": 135.7681, "rating": 4.9, "price_per_night": 820,  "currency": "USD", "features": ["Pool","Fine Dining","Onsen","River View"]},
        {"id": "hotel_aman",    "name": "Aman Kyoto",             "city": "Kyoto",    "country": "Japan", "address": "Kita Ward, Kyoto",    "lat": 35.0354, "lng": 135.7285, "rating": 4.8, "price_per_night": 1240, "currency": "USD", "features": ["Forest Garden","Onsen","Tea Ceremony"]},
        {"id": "hotel_granbell","name": "Kyoto Granbell Hotel",   "city": "Kyoto",    "country": "Japan", "address": "Gion, Kyoto",         "lat": 35.0035, "lng": 135.7751, "rating": 4.7, "price_per_night": 195,  "currency": "USD", "features": ["Great Transit","Gion Access","Café"]},
        {"id": "hotel_mimaru",  "name": "Mimaru Kyoto Nijo",      "city": "Kyoto",    "country": "Japan", "address": "Nakagyo Ward, Kyoto", "lat": 35.0141, "lng": 135.7536, "rating": 4.6, "price_per_night": 148,  "currency": "USD", "features": ["Apartment Suite","Full Kitchen","Family Friendly"]},
        {"id": "hotel_hoshi",   "name": "Hoshinoya Kyoto",        "city": "Kyoto",    "country": "Japan", "address": "Arashiyama, Kyoto",   "lat": 35.0094, "lng": 135.6703, "rating": 4.8, "price_per_night": 690,  "currency": "USD", "features": ["River Access","Hot Spring","Kaiseki"]},
    ]
    for h in hotels:
        db.collection("hotels").document(h["id"]).set(h)
    print(f"  ✓ {len(hotels)} hotels")

    # ── Ratings ──────────────────────────────────────────────────────
    ratings = [
        {"id": "user_marco_user_aria",  "uid": "user_marco", "entity_type": "user",  "entity_id": "user_aria",    "score": 4.8, "categories": {"reliability":4.8,"knowledge":4.7,"friendliness":5.0,"punctuality":4.5,"content":4.9}, "review": "Incredible travel companion.", "created_at": now(-72)},
        {"id": "user_aria_grp_himalaya","uid": "user_aria",  "entity_type": "group", "entity_id": "grp_himalaya", "score": 5.0, "categories": {"organisation":4.9,"safety":5.0,"value":4.6,"communication":4.8,"experience":4.9},    "review": "Best organised trek group I've joined.", "created_at": now(-48)},
    ]
    for r in ratings:
        db.collection("ratings").document(r["id"]).set(r)
    print(f"  ✓ {len(ratings)} ratings")

    print("\n✅ Firestore seeding complete!")
    print("   Run the app with: python run.py")
