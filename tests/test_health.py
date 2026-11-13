"""GET /health and request logging (issue #127)."""

import logging
import sys

import pytest
from support import USER, login

from app import create_app


@pytest.fixture
def app_logs(caplog):
    caplog.set_level(logging.INFO, logger="app")
    return caplog


def request_lines(caplog):
    return [r.getMessage() for r in caplog.records if r.getMessage().startswith("request ")]


def test_health_returns_ok_when_database_is_reachable(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "database": "ok"}


def test_health_returns_503_when_database_file_is_missing(tmp_path):
    missing = tmp_path / "no-such-folder" / "smashgo.sqlite3"
    client = create_app({"TESTING": True, "DATABASE_PATH": str(missing)}).test_client()

    response = client.get("/health")

    assert response.status_code == 503
    assert response.get_json() == {"status": "error", "database": "unavailable"}
    assert not missing.exists()  # the check does not create an empty database


def test_health_returns_503_when_file_is_not_a_database(tmp_path):
    broken = tmp_path / "broken.sqlite3"
    broken.write_bytes(b"this is not an sqlite file" * 100)
    client = create_app({"TESTING": True, "DATABASE_PATH": str(broken)}).test_client()

    response = client.get("/health")

    assert response.status_code == 503
    assert response.get_json() == {"status": "error", "database": "unavailable"}


def test_each_request_logs_method_path_status_and_duration(client, app_logs):
    client.get("/courts?location=Hanoi")

    lines = request_lines(app_logs)
    assert len(lines) == 1
    assert lines[0].startswith("request method=GET path=/courts status=200 duration_ms=")
    assert "Hanoi" not in lines[0]  # the query string is never logged


def test_login_does_not_write_password_or_email_to_the_log(client, app_logs):
    email, password = USER
    login(client, USER)
    client.post("/login", data={"email": email, "password": "Wrong-Password-1"})

    log_text = "\n".join(r.getMessage() for r in app_logs.records)
    assert "request method=POST path=/login" in log_text
    assert password not in log_text
    assert "Wrong-Password-1" not in log_text
    assert email not in log_text


def test_unhandled_error_is_logged_with_stack_trace(database_path, app_logs):
    app = create_app({"DATABASE_PATH": str(database_path), "SECRET_KEY": "test-only"})

    @app.get("/boom")
    def boom():
        raise RuntimeError("boom for the log test")

    response = app.test_client().get("/boom")

    assert response.status_code == 500
    error_records = [r for r in app_logs.records if r.exc_info]
    assert error_records and error_records[0].exc_info[0] is RuntimeError
    assert "request method=GET path=/boom status=500" in request_lines(app_logs)[0]


def test_logs_go_to_stdout(app):
    streams = [getattr(h, "stream", None) for h in app.logger.handlers]
    assert sys.stdout in streams or any(
        getattr(s, "name", None) == "<stdout>" for s in streams
    )
