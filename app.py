import os
import secrets

from flask import Flask, redirect, render_template, request, session, url_for

from court_service import list_active_courts
from database import get_database_path
from request_logging import init_request_logging
from routes import (
    admin_api_bp,
    auth_bp,
    bank_accounts_bp,
    bookings_bp,
    court_pages_bp,
    health_bp,
    pages_bp,
)


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(
        DATABASE_PATH=str(get_database_path()),
        SECRET_KEY=os.getenv("SECRET_KEY") or secrets.token_hex(32),
        HOST=os.getenv("HOST", "127.0.0.1"),
        PORT=int(os.getenv("PORT", "5000")),
        DEBUG=os.getenv("FLASK_DEBUG", "false").lower() == "true",
    )
    if test_config:
        app.config.update(test_config)

    # Task #127: one log line per request on stdout, and GET /health.
    init_request_logging(app)
    app.register_blueprint(health_bp)

    app.register_blueprint(auth_bp)
    app.register_blueprint(pages_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(bank_accounts_bp)
    # Task #94: Register Admin JSON endpoints for court review and status management.
    app.register_blueprint(admin_api_bp)
    # Task #95: Register public court details and availability endpoints.
    app.register_blueprint(court_pages_bp)

    @app.context_processor
    def inject_current_user():
        return {"current_user": session.get("user")}

    @app.get("/")
    def home():
        return redirect(url_for("courts"))

    @app.get("/courts")
    def courts():
        # The page searches by area only; the date and time are chosen on /book.
        location = request.args.get("location", "").strip()
        court_rows = list_active_courts(app.config["DATABASE_PATH"], location=location)
        return render_template("courts.html", courts=court_rows, location=location)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host=app.config["HOST"], port=app.config["PORT"], debug=app.config["DEBUG"])