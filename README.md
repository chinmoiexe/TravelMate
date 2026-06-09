# TravelMate Backend

Flask + Firebase + Socket.IO backend for the TravelMate travel social platform.

---

## Stack

| Layer | Technology |
|---|---|
| Web framework | Flask 3.0 |
| Real-time | Flask-SocketIO + eventlet |
| Database | Google Firestore |
| Auth | Firebase Phone Auth + Twilio Verify |
| Storage | Firebase Cloud Storage |
| OTP (fallback) | Twilio Verify |
| Rate limiting | Flask-Limiter + Redis |
| Tests | pytest |
| Container | Docker + docker-compose |

---

## Quick Start

### 1. Prerequisites
- Python 3.12+
- A Firebase project ([console.firebase.google.com](https://console.firebase.google.com))
- (Optional) Twilio account for SMS OTP fallback

### 2. Clone & install

```bash
git clone https://github.com/your-org/travelmate-backend
cd travelmate-backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env with your Firebase + Twilio credentials
```

### 4. Add Firebase service account

Download your service account JSON from:
**Firebase Console → Project Settings → Service Accounts → Generate new private key**

Save it as `config/firebase-service-account.json`.

> ⚠️  Never commit this file. It's in `.gitignore`.

### 5. Seed demo data (optional)

```bash
python scripts/seed_firestore.py
```

### 6. Run

```bash
python run.py
# API available at http://localhost:5000
# Socket.IO available at ws://localhost:5000
```

### 7. Docker (alternative)

```bash
docker-compose up --build
```

---

## Project Structure

```
travelmate-backend/
├── run.py                          # Entry point
├── app/
│   ├── __init__.py                 # App factory + SocketIO init
│   ├── routes/
│   │   ├── auth.py                 # POST /api/auth/...
│   │   ├── feed.py                 # GET/POST /api/feed/...
│   │   ├── groups.py               # /api/groups/...
│   │   ├── chat.py                 # /api/chat/...
│   │   ├── tracking.py             # /api/tracking/...
│   │   ├── hotels.py               # /api/hotels/...
│   │   ├── profile.py              # /api/profile/...
│   │   └── ratings.py              # /api/ratings/...
│   ├── services/
│   │   ├── auth_service.py         # OTP send/verify logic
│   │   ├── socket_service.py       # All Socket.IO events
│   │   ├── feed_service.py         # Firestore feed queries
│   │   ├── groups_service.py
│   │   ├── chat_service.py
│   │   ├── tracking_service.py
│   │   ├── hotels_service.py
│   │   ├── profile_service.py
│   │   └── ratings_service.py
│   ├── models/
│   │   └── schema.py               # Firestore document schemas
│   └── utils/
│       ├── firebase_client.py      # Firestore/Auth/Storage singletons
│       ├── auth_helpers.py         # @auth_required decorator
│       └── responses.py            # success() / error() helpers
├── config/
│   ├── settings.py                 # Dev/Prod/Test config
│   └── firebase-service-account.json   # ← you provide this
├── scripts/
│   └── seed_firestore.py           # Demo data seeder
├── tests/
│   └── test_api.py
├── .env.example
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## REST API Reference

### Auth

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/send-otp` | Send OTP to phone number |
| POST | `/api/auth/verify-otp` | Verify OTP, receive token |
| GET | `/api/auth/me` | Get current user |
| POST | `/api/auth/logout` | Revoke tokens |

**Send OTP**
```json
POST /api/auth/send-otp
{ "phone": "+15551234567" }
```

**Verify OTP**
```json
POST /api/auth/verify-otp
{ "phone": "+15551234567", "code": "428193" }

Response:
{
  "data": {
    "token": "<firebase_custom_token>",
    "user": { "uid": "...", "display_name": "..." }
  }
}
```

### Feed

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/feed/?page=1&category=Mountains` | Home feed |
| GET | `/api/feed/stories` | Active stories |
| POST | `/api/feed/posts` | Create post |
| DELETE | `/api/feed/posts/:id` | Delete own post |
| POST | `/api/feed/posts/:id/like` | Toggle like |
| POST | `/api/feed/posts/:id/save` | Toggle bookmark |
| GET | `/api/feed/trending` | Trending destinations |
| GET | `/api/feed/suggestions` | Suggested travelers |

### Groups

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/groups/?category=Adventure` | List groups |
| POST | `/api/groups/` | Create group |
| GET | `/api/groups/:id` | Get group |
| PATCH | `/api/groups/:id` | Update group (owner) |
| DELETE | `/api/groups/:id` | Delete group (owner) |
| POST | `/api/groups/:id/join` | Join / leave toggle |
| GET | `/api/groups/:id/members` | List members |

### Chat

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/chat/conversations` | List conversations |
| GET | `/api/chat/conversations/:id/messages` | Get messages |
| POST | `/api/chat/conversations/:id/messages` | Send message |
| DELETE | `/api/chat/messages/:id` | Delete message |

### Tracking

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/tracking/` | List journeys |
| POST | `/api/tracking/` | Add journey |
| PATCH | `/api/tracking/:id` | Update journey |
| DELETE | `/api/tracking/:id` | Delete journey |
| GET | `/api/tracking/live-pins` | Map pin data |

### Hotels

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/hotels/search?destination=Kyoto&checkin=2026-05-15&checkout=2026-05-19` | Search |
| GET | `/api/hotels/:id` | Hotel detail |
| POST | `/api/hotels/:id/book` | Create booking |

### Profile

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/profile/:uid` | Get profile |
| PATCH | `/api/profile/me` | Update own profile |
| POST | `/api/profile/:uid/follow` | Follow user |
| DELETE | `/api/profile/:uid/follow` | Unfollow user |
| GET | `/api/profile/:uid/followers` | Followers list |
| GET | `/api/profile/:uid/following` | Following list |

### Ratings

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/ratings/user/:uid` | User ratings |
| GET | `/api/ratings/group/:group_id` | Group ratings |
| GET | `/api/ratings/summary/user/:uid` | Rating summary |
| POST | `/api/ratings/` | Submit rating |

---

## Socket.IO Events

Connect with: `ws://localhost:5000?uid=<user_uid>`

### Client → Server

| Event | Payload | Description |
|---|---|---|
| `join_conversation` | `{ convo_id }` | Subscribe to chat room |
| `leave_conversation` | `{ convo_id }` | Unsubscribe |
| `send_message` | `{ convo_id, text, attachment_url? }` | Send a message |
| `typing_start` | `{ convo_id }` | Show typing indicator |
| `typing_stop` | `{ convo_id }` | Hide typing indicator |
| `update_presence` | `{ online: bool }` | Update online status |

### Server → Client

| Event | Payload | Description |
|---|---|---|
| `new_message` | `{ convo_id, message }` | New message in room |
| `typing` | `{ convo_id, uid, is_typing }` | Typing state change |
| `presence_update` | `{ uid, online, last_seen }` | User presence change |
| `tracking_update` | `{ journey_id, progress, status }` | Journey status change |
| `notification` | `{ type, payload }` | Push notification |

---

## Firestore Collections

```
users/                  ← user profiles + presence
posts/                  ← feed posts
stories/                ← 24h stories
post_likes/             ← post_id + uid compound key
post_saves/             ← bookmarks
groups/                 ← travel groups
group_members/          ← group_id + uid membership
conversations/          ← chat threads (DM + group)
messages/               ← individual messages
journeys/               ← flight / train / hotel tracking
hotels/                 ← hotel catalogue
bookings/               ← hotel bookings
ratings/                ← per-user, per-group ratings
rating_summaries/       ← pre-aggregated averages
follows/                ← follow graph
trending_destinations/  ← updated by cron job
```

---

## Authentication Flow

```
1. Client  →  POST /api/auth/send-otp  { phone }
2. Server  →  Twilio Verify sends SMS OTP
3. Client  →  POST /api/auth/verify-otp  { phone, code }
4. Server  →  Firebase creates/gets user, returns custom token
5. Client  →  signInWithCustomToken(token)  [Firebase SDK]
6. Client  →  all subsequent requests use Firebase ID token
              Authorization: Bearer <firebase_id_token>
```

---

## Running Tests

```bash
pytest tests/ -v
```

---

## Deployment

**Cloud Run (recommended)**
```bash
gcloud run deploy travelmate-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars FLASK_ENV=production
```

Use Application Default Credentials on Cloud Run — no service account JSON needed.
