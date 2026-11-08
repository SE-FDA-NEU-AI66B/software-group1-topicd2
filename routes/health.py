import sqlite3

from flask import Blueprint, current_app, jsonify

from database import check_database

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health():
    try:
        check_database(current_app.config["DATABASE_PATH"])
    except sqlite3.Error:
        current_app.logger.exception("Health check failed: database unavailable")
        return jsonify(status="error", database="unavailable"), 503
    return jsonify(status="ok", database="ok"), 200
