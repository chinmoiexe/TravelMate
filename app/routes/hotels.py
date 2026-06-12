from flask import Blueprint, request, g
from app.utils.responses import success, error, paginated
from app.utils.auth_helpers import auth_required
from app.services.hotels_service import search_hotels, get_hotel, create_booking

hotels_bp = Blueprint("hotels", __name__)

@hotels_bp.get("/search")
@auth_required
def route_search():
    params = {
        "destination": request.args.get("destination", ""),
        "checkin":     request.args.get("checkin"),
        "checkout":    request.args.get("checkout"),
        "guests":      int(request.args.get("guests", 1)),
        "page":        int(request.args.get("page", 1)),
        "page_size":   int(request.args.get("page_size", 20)),
    }
    items, total = search_hotels(**params)
    return paginated(items, params["page"], params["page_size"], total)

@hotels_bp.get("/<hotel_id>")
@auth_required
def route_hotel(hotel_id):
    hotel = get_hotel(hotel_id)
    return (success(hotel) if hotel else error("Not found", 404))

@hotels_bp.post("/<hotel_id>/book")
@auth_required
def route_book(hotel_id):
    body    = request.get_json(silent=True) or {}
    booking = create_booking(hotel_id, g.uid, body)
    if not booking:
        return error("Booking failed — check dates and availability")
    return success(booking, status=201)
