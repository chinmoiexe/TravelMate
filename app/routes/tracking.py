from flask import Blueprint, request, g
from app.utils.responses import success, error
from app.utils.auth_helpers import auth_required
from app.services.tracking_service import (
    get_journeys, add_journey, update_journey, delete_journey, get_live_pins,
)

tracking_bp = Blueprint("tracking", __name__)

@tracking_bp.get("/")
@auth_required
def route_journeys():
    return success(get_journeys(g.uid))

@tracking_bp.post("/")
@auth_required
def route_add():
    body = request.get_json(silent=True) or {}
    j = add_journey(g.uid, body)
    return success(j, status=201)

@tracking_bp.patch("/<journey_id>")
@auth_required
def route_update(journey_id):
    body = request.get_json(silent=True) or {}
    ok = update_journey(journey_id, g.uid, body)
    return (success(message="Updated") if ok else error("Not found", 404))

@tracking_bp.delete("/<journey_id>")
@auth_required
def route_delete(journey_id):
    ok = delete_journey(journey_id, g.uid)
    return (success(message="Deleted") if ok else error("Not found", 404))

@tracking_bp.get("/live-pins")
@auth_required
def route_pins():
    return success(get_live_pins(g.uid))
