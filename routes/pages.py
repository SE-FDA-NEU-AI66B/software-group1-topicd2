from functools import wraps

from flask import Blueprint, redirect, render_template, request, session, url_for

from routes.auth import default_url_for_role

pages_bp = Blueprint("pages", __name__)


def role_required(required_role: str):
    def decorator(view_function):
        @wraps(view_function)
        def wrapped(*args, **kwargs):
            current_user = session.get("user")
            if not current_user:
                next_url = request.full_path.removesuffix("?")
                return redirect(url_for("auth.login", next=next_url))

            if current_user.get("role") != required_role:
                return (
                    render_template(
                        "pages/forbidden.html",
                        default_url=default_url_for_role(current_user["role"]),
                    ),
                    403,
                )

            return view_function(*args, **kwargs)

        return wrapped

    return decorator


@pages_bp.get("/my-bookings")
@role_required("USER")
def my_bookings():
    return render_template("pages/my_bookings.html")


@pages_bp.get("/manager/courts")
@role_required("MANAGER")
def manager_courts():
    return render_template("pages/not_supported.html")


@pages_bp.get("/admin/courts")
@role_required("ADMIN")
def admin_courts():
    return render_template("pages/not_supported.html")