import re
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any

from database import get_db_connection
from werkzeug.security import check_password_hash, generate_password_hash

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_registration(full_name: str, email: str, password: str) -> str | None:
    if (
        not full_name.strip()
        or not EMAIL_PATTERN.fullmatch(email.strip())
        or len(password) < 8
    ):
        return "INVALID_INPUT"
    return None


def register_user(
    database_path: str | Path,
    full_name: str,
    email: str,
    password: str,
    phone: str = "",
) -> tuple[dict[str, Any] | None, str | None]:
    error_code = validate_registration(full_name, email, password)
    if error_code:
        return None, error_code

    clean_name = full_name.strip()
    clean_email = email.strip().lower()
    clean_phone = phone.strip() or None

    with closing(get_db_connection(database_path)) as connection, connection:
        existing_user = connection.execute(
            "SELECT UserID FROM Users WHERE Email = ? COLLATE NOCASE",
            (clean_email,),
        ).fetchone()
        if existing_user:
            return None, "EMAIL_EXISTS"

        try:
            cursor = connection.execute(
                """
                INSERT INTO Users (FullName, Email, PasswordHash, Phone, Role)
                VALUES (?, ?, ?, ?, 'USER')
                """,
                (
                    clean_name,
                    clean_email,
                    generate_password_hash(password),
                    clean_phone,
                ),
            )
        except sqlite3.IntegrityError:
            existing_user = connection.execute(
                "SELECT UserID FROM Users WHERE Email = ? COLLATE NOCASE",
                (clean_email,),
            ).fetchone()
            if existing_user:
                return None, "EMAIL_EXISTS"
            raise

        user = connection.execute(
            "SELECT UserID, FullName, Email, Role FROM Users WHERE UserID = ?",
            (cursor.lastrowid,),
        ).fetchone()
        return {
            "user_id": user["UserID"],
            "full_name": user["FullName"],
            "email": user["Email"],
            "role": user["Role"],
        }, None


def authenticate_user(
    database_path: str | Path,
    email: str,
    password: str,
) -> dict[str, Any] | None:
    with closing(get_db_connection(database_path)) as connection, connection:
        user = connection.execute(
            """
            SELECT UserID, FullName, Email, PasswordHash, Role
            FROM Users
            WHERE Email = ? COLLATE NOCASE
            """,
            (email.strip(),),
        ).fetchone()

    if user is None:
        return None

    try:
        password_matches = check_password_hash(user["PasswordHash"], password)
    except (TypeError, ValueError):
        password_matches = False

    if not password_matches:
        return None

    return {
        "user_id": user["UserID"],
        "full_name": user["FullName"],
        "email": user["Email"],
        "role": user["Role"],
    }