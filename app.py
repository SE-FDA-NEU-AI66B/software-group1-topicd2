import os
import secrets

from flask import Flask, redirect, render_template, request, session, url_for

import clock
from booking_service import BookingError
from court_service import list_active_courts
from database import get_database_path
from routes import (
    admin_api_bp,
    auth_bp,
    bank_accounts_bp,
    bookings_bp,
    court_pages_bp,
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
        filters = {
            "date": request.args.get("date", "").strip(),
            "start_time": request.args.get("startTime", "").strip(),
            "end_time": request.args.get("endTime", "").strip(),
            "location": request.args.get("location", "").strip(),
        }
        filter_error = None
        try:
            court_rows = list_active_courts(
                app.config["DATABASE_PATH"],
                filters["date"],
                filters["start_time"],
                filters["end_time"],
                filters["location"],
            )
        except BookingError:
            court_rows = []
            filter_error = (
                "Để lọc theo giờ, hãy chọn ngày, giờ bắt đầu và giờ kết thúc hợp lệ "
                "(tối thiểu 1 giờ, theo bước 30 phút)."
            )
        return render_template(
            "courts.html",
            courts=court_rows,
            filters=filters,
            filter_error=filter_error,
            today=clock.today().isoformat(),
        )

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host=app.config["HOST"], port=app.config["PORT"], debug=app.config["DEBUG"])