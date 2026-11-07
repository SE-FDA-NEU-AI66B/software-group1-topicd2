"""Guards for the production deploy configuration (issue #126).

render.yaml is read by Render, not by the app, so nothing else fails if a
later change breaks it. These tests read it as text (no YAML dependency).
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RENDER_YAML = (ROOT / "render.yaml").read_text(encoding="utf-8")


def _start_command() -> str:
    for line in RENDER_YAML.splitlines():
        if line.strip().startswith("startCommand:"):
            return line.split(":", 1)[1].strip()
    raise AssertionError("render.yaml has no startCommand")


def test_start_command_seeds_database_before_gunicorn():
    command = _start_command()
    assert command.index("python init_db.py") < command.index("gunicorn")
    assert "&&" in command  # the app does not start if seeding fails


def test_gunicorn_listens_on_all_interfaces_and_render_port():
    command = _start_command()
    assert "gunicorn app:app" in command
    assert "--bind 0.0.0.0:$PORT" in command


def test_deploys_only_after_ci_is_green():
    assert "autoDeployTrigger: checksPass" in RENDER_YAML
    assert "branch: main" in RENDER_YAML


def test_production_runs_without_debug_and_with_generated_secret():
    assert 'key: FLASK_DEBUG\n        value: "false"' in RENDER_YAML
    assert "key: SECRET_KEY\n        generateValue: true" in RENDER_YAML


def test_gunicorn_is_a_runtime_dependency():
    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8").lower()
    assert "gunicorn" in requirements


def test_wsgi_entry_point_serves_the_first_screen(tmp_path):
    from init_db import initialize_database
    from app import create_app

    database_path = tmp_path / "deploy.sqlite3"
    initialize_database(database_path)
    client = create_app({"DATABASE_PATH": str(database_path), "TESTING": True}).test_client()

    assert client.get("/").status_code == 302
    response = client.get("/courts")
    assert response.status_code == 200
    assert "court-detail-link" in response.get_data(as_text=True)
