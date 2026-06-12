from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
from config.settings import config

socketio = SocketIO()

def create_app(config_name="development"):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    CORS(app, origins=app.config["CORS_ORIGINS"], supports_credentials=True)
    socketio.init_app(
        app,
        cors_allowed_origins=app.config["CORS_ORIGINS"],
        async_mode="eventlet",
        logger=False,
        engineio_logger=False,
    )

    # Register blueprints
    from app.routes.auth     import auth_bp
    from app.routes.feed     import feed_bp
    from app.routes.groups   import groups_bp
    from app.routes.chat     import chat_bp
    from app.routes.tracking import tracking_bp
    from app.routes.hotels   import hotels_bp
    from app.routes.profile  import profile_bp
    from app.routes.ratings  import ratings_bp

    app.register_blueprint(auth_bp,     url_prefix="/api/auth")
    app.register_blueprint(feed_bp,     url_prefix="/api/feed")
    app.register_blueprint(groups_bp,   url_prefix="/api/groups")
    app.register_blueprint(chat_bp,     url_prefix="/api/chat")
    app.register_blueprint(tracking_bp, url_prefix="/api/tracking")
    app.register_blueprint(hotels_bp,   url_prefix="/api/hotels")
    app.register_blueprint(profile_bp,  url_prefix="/api/profile")
    app.register_blueprint(ratings_bp,  url_prefix="/api/ratings")

    # Register Socket.IO events
    from app.services import socket_service  # noqa: F401

    @app.get("/health")
    def health():
        return {"status": "ok", "service": "TravelMate API"}

    return app
