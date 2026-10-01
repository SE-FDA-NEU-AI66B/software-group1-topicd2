import os
import sqlite3
from contextlib import closing

from flask import Flask, render_template

from database import get_database_path


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(
        DATABASE_PATH=str(get_database_path()),
        HOST=os.getenv("HOST", "127.0.0.1"),
        PORT=int(os.getenv("PORT", "5000")),
        DEBUG=os.getenv("FLASK_DEBUG", "false").lower() == "true",
    )
    if test_config:
        app.config.update(test_config)

    @app.get("/courts")
    def courts():
        with closing(sqlite3.connect(app.config["DATABASE_PATH"])) as connection:
            connection.row_factory = sqlite3.Row
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