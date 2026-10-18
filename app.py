import os
import secrets
from contextlib import closing

from flask import Flask, redirect, render_template, session, url_for

from database import get_database_path, get_db_connection
from routes import auth_bp, pages_bp


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

    @app.context_processor
    def inject_current_user():
        return {"current_user": session.get("user")}

    @app.get("/")
    def home():
        return redirect(url_for("courts"))

    @app.get("/courts")
    def courts():
        with closing(get_db_connection(app.config["DATABASE_PATH"])) as connection:
            court_rows = connection.execute(
                """
                SELECT Court.CourtID, Court.CourtName, Court.Location,
                       Court.Description, Court.PricePerHour, Court.OpenTime,
                       Court.CloseTime,
                       (
                           SELECT Court_Image.Url
                           FROM Court_Image
                           WHERE Court_Image.CourtID = Court.CourtID
                           ORDER BY Court_Image.SortOrder, Court_Image.ImageID
                           LIMIT 1
                       ) AS ImageUrl
                FROM Court
                WHERE Court.Status = 'ACTIVE'
                ORDER BY Court.CourtID
                """
            ).fetchall()

        return render_template("courts.html", courts=court_rows)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host=app.config["HOST"], port=app.config["PORT"], debug=app.config["DEBUG"])