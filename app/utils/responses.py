from flask import jsonify


def success(data=None, message="OK", status=200):
    body = {"success": True, "message": message}
    if data is not None:
        body["data"] = data
    return jsonify(body), status


def error(message="An error occurred", status=400, details=None):
    body = {"success": False, "error": message}
    if details:
        body["details"] = details
    return jsonify(body), status


def paginated(items: list, page: int, page_size: int, total: int):
    return jsonify({
        "success": True,
        "data": items,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "pages": -(-total // page_size),  # ceil division
        },
    }), 200


# ------------------------------------------------------------------ #
#  Register with app                                                   #
# ------------------------------------------------------------------ #

def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(e):
        return error(str(e), 400)

    @app.errorhandler(401)
    def unauthorized(e):
        return error("Unauthorized", 401)

    @app.errorhandler(403)
    def forbidden(e):
        return error("Forbidden", 403)

    @app.errorhandler(404)
    def not_found(e):
        return error("Not found", 404)

    @app.errorhandler(429)
    def rate_limited(e):
        return error("Rate limit exceeded — slow down!", 429)

    @app.errorhandler(500)
    def server_error(e):
        app.logger.exception(e)
        return error("Internal server error", 500)
