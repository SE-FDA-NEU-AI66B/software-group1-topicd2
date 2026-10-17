from urllib.parse import urlsplit

from flask import Blueprint, current_app, redirect, render_template, request, session, url_for

from auth import authenticate_user, register_user
from errors import user_message

auth_bp = Blueprint("auth", __name__)


def safe_next_url(candidate: str | None) -> str | None:
    if (
        not candidate
        or not candidate.startswith("/")
        or candidate.startswith("//")
        or "\\" in candidate
        or any(ord(character) < 32 for character in candidate)
    ):
        return None

    parsed_url = urlsplit(candidate)
    if parsed_url.scheme or parsed_url.netloc:
        return None
    return candidate


def default_url_for_role(role: str) -> str:
    endpoints = {
        "USER": "pages.my_bookings",
        "MANAGER": "pages.manager_courts",
        "ADMIN": "pages.admin_courts",
    }
    endpoint = endpoints.get(role)
    return url_for(endpoint) if endpoint else url_for("courts")


def _redirect_for_role(role: str, next_url: str | None = None):
    if role == "USER" and next_url:
        return redirect(next_url)
    return redirect(default_url_for_role(role))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    current_user = session.get("user")
    if current_user:
        return redirect(default_url_for_role(current_user["role"]))

    next_url = safe_next_url(request.values.get("next"))
    error_message = None
    if request.method == "POST":
        user = authenticate_user(
            current_app.config["DATABASE_PATH"],
            request.form.get("email", ""),
            request.form.get("password", ""),
        )
        if user is None:
            error_message = user_message("INVALID_CREDENTIALS")
        else:
            session.clear()
            session["user"] = user
            return _redirect_for_role(user["role"], next_url)

    return render_template(
        "auth/login.html",
        error_message=error_message,
        next_url=next_url,
    )


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    current_user = session.get("user")
    if current_user:
        return redirect(default_url_for_role(current_user["role"]))

    next_url = safe_next_url(request.values.get("next"))
    error_message = None
    if request.method == "POST":
        user, error_code = register_user(
            current_app.config["DATABASE_PATH"],
            request.form.get("full_name", ""),
            request.form.get("email", ""),
            request.form.get("password", ""),
            request.form.get("phone", ""),
        )
        if error_code:
            error_message = user_message(error_code)
        else:
            session.clear()
            session["user"] = user
            return _redirect_for_role(user["role"], next_url)

    return render_template(
        "auth/register.html",
        error_message=error_message,
        next_url=next_url,
    )


@auth_bp.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("courts"))