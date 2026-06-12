"""
models/schema.py
----------------
Firestore Collection Schemas
Each class is a typed dict / dataclass representing a Firestore document.
These are NOT ORM models — they serve as documentation and can be used
for validation (with Pydantic or marshmallow if desired).
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class User:
    """Collection: users/{uid}"""
    uid:          str
    phone:        str
    username:     str
    display_name: str
    avatar_url:   str
    banner_url:   str = ""
    bio:          str = ""
    tags:         list = field(default_factory=list)    # ["Mountains", "Diving"]
    countries:    list = field(default_factory=list)    # ISO country codes visited
    followers:    int  = 0
    following:    int  = 0
    posts:        int  = 0
    online:       bool = False
    last_seen:    str  = ""
    created_at:   str  = ""


@dataclass
class Post:
    """Collection: posts/{post_id}"""
    id:          str
    uid:         str                        # author's UID
    caption:     str
    location:    str
    category:    str                        # Mountains | Beaches | Cities | ...
    media_urls:  list = field(default_factory=list)
    tags:        list = field(default_factory=list)
    likes:       int  = 0
    saves:       int  = 0
    comments:    int  = 0
    created_at:  str  = ""


@dataclass
class Story:
    """Collection: stories/{story_id}"""
    id:         str
    uid:        str
    media_url:  str
    caption:    str = ""
    expires_at: str = ""                    # ISO datetime (24h from creation)
    viewers:    list = field(default_factory=list)
    created_at: str  = ""


@dataclass
class Group:
    """Collection: groups/{group_id}"""
    id:           str
    owner_uid:    str
    name:         str
    description:  str
    category:     str
    banner_url:   str  = ""
    is_private:   bool = False
    requires_approval: bool = False
    member_limit: Optional[int] = None
    member_count: int  = 0
    created_at:   str  = ""


@dataclass
class GroupMember:
    """Collection: group_members/{group_id}_{uid}"""
    group_id:  str
    uid:       str
    role:      str = "member"               # owner | admin | member
    joined_at: str = ""
    status:    str = "active"               # active | pending | banned


@dataclass
class Conversation:
    """Collection: conversations/{convo_id}"""
    id:              str
    participants:    list                   # list of UIDs
    is_group:        bool  = False
    group_id:        Optional[str] = None
    last_message:    str   = ""
    last_message_at: str   = ""
    unread:          dict  = field(default_factory=dict)  # {uid: count}
    created_at:      str   = ""


@dataclass
class Message:
    """Collection: messages/{msg_id}"""
    id:             str
    convo_id:       str
    sender_uid:     str
    text:           str  = ""
    attachment_url: Optional[str] = None
    read_by:        list = field(default_factory=list)
    created_at:     str  = ""


@dataclass
class Journey:
    """Collection: journeys/{journey_id}"""
    id:             str
    uid:            str
    type:           str                     # flight | train | hotel | bus
    # Flight / Train specific
    origin:         str  = ""
    destination:    str  = ""
    carrier:        str  = ""
    flight_number:  str  = ""
    departure_time: str  = ""
    arrival_time:   str  = ""
    terminal:       str  = ""
    gate:           str  = ""
    seat:           str  = ""
    # Hotel specific
    hotel_name:     str  = ""
    checkin:        str  = ""
    checkout:       str  = ""
    booking_ref:    str  = ""
    # Status
    status:         str  = "scheduled"      # scheduled|boarding|active|delayed|landed|completed
    progress_pct:   int  = 0
    delay_minutes:  int  = 0
    # Coordinates (for live map)
    current_lat:    Optional[float] = None
    current_lng:    Optional[float] = None
    created_at:     str  = ""


@dataclass
class Hotel:
    """Collection: hotels/{hotel_id}"""
    id:           str
    name:         str
    city:         str
    country:      str
    address:      str
    lat:          float = 0.0
    lng:          float = 0.0
    rating:       float = 0.0
    price_per_night: float = 0.0
    currency:     str  = "USD"
    features:     list = field(default_factory=list)
    images:       list = field(default_factory=list)
    description:  str  = ""


@dataclass
class Booking:
    """Collection: bookings/{booking_id}"""
    id:         str
    hotel_id:   str
    uid:        str
    checkin:    str
    checkout:   str
    guests:     int  = 1
    total_price: float = 0.0
    status:     str  = "confirmed"          # confirmed | cancelled | completed
    booking_ref: str = ""
    created_at: str  = ""


@dataclass
class Rating:
    """Collection: ratings/{uid}_{entity_type}_{entity_id}"""
    id:          str
    uid:         str
    entity_type: str                        # user | group
    entity_id:   str
    score:       float                      # 0.0 – 5.0
    categories:  dict = field(default_factory=dict)  # {reliability: 4.5, ...}
    review:      str  = ""
    created_at:  str  = ""


@dataclass
class RatingSummary:
    """Collection: rating_summaries/{entity_type}_{entity_id}"""
    entity_type: str
    entity_id:   str
    average:     float = 0.0
    count:       int   = 0
    updated_at:  str   = ""


@dataclass
class Follow:
    """Collection: follows/{follower_uid}_{following_uid}"""
    follower:   str
    following:  str
    created_at: str = ""


@dataclass
class TrendingDestination:
    """Collection: trending_destinations/{id}"""
    id:          str
    name:        str
    country:     str
    region:      str
    emoji:       str
    growth_pct:  float = 0.0
    category:    str   = ""
    updated_at:  str   = ""
