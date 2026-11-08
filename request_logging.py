"""Request logging to stdout, where Render reads the logs.

One line per request: method, path, status and time in ms. Only the path is
logged: never the query string, form data, JSON body, headers or cookies, so
passwords, tokens, card numbers and emails cannot reach the log.
Unhandled errors are logged with their stack trace by Flask itself.
"""

import logging
import sys
import time

from flask import Flask, g, request
from flask.logging import default_handler

LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"


def init_request_logging(app: Flask) -> None:
    app.logger.removeHandler(default_handler)
    if not any(getattr(h, "smashgo_stdout", False) for h in app.logger.handlers):
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(LOG_FORMAT))
        handler.smashgo_stdout = True
        app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)

    @app.before_request
    def start_timer():
        g.request_started = time.perf_counter()

    @app.after_request
    def log_request(response):
        started = g.pop("request_started", None)
        duration_ms = (time.perf_counter() - started) * 1000 if started else 0.0
        app.logger.info(
            "request method=%s path=%s status=%s duration_ms=%.1f",
            request.method,
            request.path,
            response.status_code,
            duration_ms,
        )
        return response
