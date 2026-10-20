import sqlite3

import pytest

from app import create_app
from init_db import initialize_database

DEMO_ADMIN = ("admin@smashgo.local", "AdminTest123!")
DEMO_USER = ("user@smashgo.local", "UserTest123!")
DEMO_MANAGER = ("walking-skeleton-manager@smashgo.local", "ManagerTest123!")


# Task #94: Build an isolated database and Flask client with the Admin demo requests seeded.
@pytest.fixture
def admin_environment(tmp_path):
    database_path = tmp_path / "smashgo.sqlite3"
    initialize_database(database_path)
    app = create_app({"TESTING": True, "DATABASE_PATH": str(database_path)})
    return app.test_client(), database_path


# Task #94: Authenticate a test client with one of the seeded roles.
def login(client, account):
    email, password = account
    assert client.post("/login", data={"email": email, "password": password}).status_code == 302


# Task #94: Confirm the Admin page uses its dedicated rendered template.
def test_admin_page_renders_court_management_workspace(admin_environment):
    client, _ = admin_environment
    login(client, DEMO_ADMIN)

    response = client.get("/admin/courts")

    assert response.status_code == 200
    assert "Yêu cầu chờ duyệt" in response.get_data(as_text=True)
    assert "Tất cả sân" in response.get_data(as_text=True)


# Task #94: Keep unauthenticated and non-Admin callers out of all protected Admin APIs.
@pytest.mark.parametrize(
    ("account", "expected_status", "expected_code"),
    [
        (None, 401, "UNAUTHENTICATED"),
        (DEMO_USER, 403, "ADMIN_REQUIRED"),
        (DEMO_MANAGER, 403, "ADMIN_REQUIRED"),
    ],
)
def test_admin_apis_require_admin_role(
    admin_environment, account, expected_status, expected_code
):
    client, _ = admin_environment
    if account:
        login(client, account)

    response = client.get("/api/admin/courts")

    assert response.status_code == expected_status
    assert response.get_json()["code"] == expected_code


# Task #94: Return all court statuses and upcoming booking counts to Admins.
def test_admin_court_list_includes_disabled_courts_and_images(admin_environment):
    client, database_path = admin_environment
    login(client, DEMO_ADMIN)
    with sqlite3.connect(database_path) as connection:
        connection.execute("UPDATE Court SET Status = 'DISABLED' WHERE CourtID = 12")

    response = client.get("/api/admin/courts")

    assert response.status_code == 200
    courts = response.get_json()
    assert len(courts) == 12
    first_court = next(court for court in courts if court["courtId"] == 1)
    disabled_court = next(court for court in courts if court["courtId"] == 12)
    assert first_court["upcomingBookings"] == 1
    assert first_court["images"][0]["url"].startswith("https://")
    assert disabled_court["status"] == "DISABLED"


# Task #94: List only pending requests by default and reject arbitrary status filter values.
def test_court_request_list_defaults_to_pending_and_validates_filter(admin_environment):
    client, _ = admin_environment
    login(client, DEMO_ADMIN)

    response = client.get("/api/admin/court-requests")
    invalid_response = client.get("/api/admin/court-requests?status=anything")

    assert response.status_code == 200
    assert len(response.get_json()) == 2
    assert all(request["status"] == "PENDING" for request in response.get_json())
    assert response.get_json()[0]["images"][0]["url"].startswith("https://")
    assert invalid_response.status_code == 400
    assert invalid_response.get_json()["code"] == "INVALID_STATUS_FILTER"


# Task #94: Include prior decisions when the Admin requests all court requests.
def test_court_request_list_can_filter_all_statuses(admin_environment):
    client, _ = admin_environment
    login(client, DEMO_ADMIN)
    request_id = client.get("/api/admin/court-requests").get_json()[0]["requestId"]
    assert client.post(
        f"/api/admin/court-requests/{request_id}/review",
        json={"decision": "REJECTED", "rejectReason": "Thiếu thông tin"},
    ).status_code == 200

    response = client.get("/api/admin/court-requests?status=ALL")

    assert response.status_code == 200
    assert {item["status"] for item in response.get_json()} == {"PENDING", "REJECTED"}


# Task #94: Approve a request atomically, create its active court and copy request images.
def test_approving_request_creates_court_and_copies_images(admin_environment):
    client, database_path = admin_environment
    login(client, DEMO_ADMIN)
    request_data = client.get("/api/admin/court-requests").get_json()[0]

    response = client.post(
        f"/api/admin/court-requests/{request_data['requestId']}/review",
        json={"decision": "APPROVED"},
    )

    assert response.status_code == 200
    result = response.get_json()
    assert result["status"] == "APPROVED"
    assert result["reviewedBy"] == 4
    with sqlite3.connect(database_path) as connection:
        court = connection.execute(
            "SELECT ManagerID, CourtName, Status FROM Court WHERE CourtID = ?",
            (result["courtId"],),
        ).fetchone()
        request_status = connection.execute(
            "SELECT Status, ReviewedBy FROM Court_Request WHERE RequestID = ?",
            (request_data["requestId"],),
        ).fetchone()
        copied_images = connection.execute(
            "SELECT Url, SortOrder FROM Court_Image WHERE CourtID = ?",
            (result["courtId"],),
        ).fetchall()
    assert court == (request_data["managerId"], request_data["courtName"], "ACTIVE")
    assert request_status == ("APPROVED", 4)
    assert copied_images == [(request_data["images"][0]["url"], 0)]


# Task #94: Require a rejection reason and prevent a reviewed request from being processed twice.
def test_rejection_requires_reason_and_review_is_single_use(admin_environment):
    client, database_path = admin_environment
    login(client, DEMO_ADMIN)
    request_id = client.get("/api/admin/court-requests").get_json()[0]["requestId"]

    missing_reason = client.post(
        f"/api/admin/court-requests/{request_id}/review",
        json={"decision": "REJECTED"},
    )
    rejected = client.post(
        f"/api/admin/court-requests/{request_id}/review",
        json={"decision": "REJECTED", "rejectReason": "Thông tin chưa đầy đủ"},
    )
    repeated = client.post(
        f"/api/admin/court-requests/{request_id}/review",
        json={"decision": "APPROVED"},
    )

    assert missing_reason.status_code == 400
    assert missing_reason.get_json()["code"] == "INVALID_DECISION"
    assert rejected.status_code == 200
    assert rejected.get_json()["status"] == "REJECTED"
    assert repeated.status_code == 409
    assert repeated.get_json()["code"] == "REQUEST_ALREADY_REVIEWED"
    with sqlite3.connect(database_path) as connection:
        notification = connection.execute(
            """
            SELECT Title, Message, Type FROM Notification
            WHERE UserID = (
                SELECT ManagerID FROM Court_Request WHERE RequestID = ?
            )
            ORDER BY NotificationID DESC LIMIT 1
            """,
            (request_id,),
        ).fetchone()
    assert notification[2] == "COURT_REQUEST_RESULT"
    assert "Thông tin chưa đầy đủ" in notification[1]


# Task #94: Report a clear not-found error for review requests that do not exist.
def test_review_nonexistent_request_returns_not_found(admin_environment):
    client, _ = admin_environment
    login(client, DEMO_ADMIN)

    response = client.post(
        "/api/admin/court-requests/9999/review",
        json={"decision": "APPROVED"},
    )

    assert response.status_code == 404
    assert response.get_json()["code"] == "REQUEST_NOT_FOUND"


# Task #94: Prevent disabling a court that has a confirmed future booking.
def test_disabling_court_with_upcoming_booking_returns_conflict(admin_environment):
    client, _ = admin_environment
    login(client, DEMO_ADMIN)

    response = client.patch("/api/admin/courts/1/status", json={"status": "DISABLED"})

    assert response.status_code == 409
    assert response.get_json()["code"] == "COURT_HAS_UPCOMING_BOOKINGS"


# Task #94: Change status for an unoccupied court and validate status input.
def test_admin_can_disable_and_reactivate_unoccupied_court(admin_environment):
    client, _ = admin_environment
    login(client, DEMO_ADMIN)

    disabled = client.patch("/api/admin/courts/12/status", json={"status": "DISABLED"})
    invalid = client.patch("/api/admin/courts/12/status", json={"status": "UNKNOWN"})
    active = client.patch("/api/admin/courts/12/status", json={"status": "ACTIVE"})

    assert disabled.status_code == 200
    assert disabled.get_json() == {"courtId": 12, "status": "DISABLED"}
    assert invalid.status_code == 400
    assert invalid.get_json()["code"] == "INVALID_STATUS"
    assert active.status_code == 200
    assert active.get_json()["status"] == "ACTIVE"


# Task #94: Make Admin demo requests safe to seed again without duplicating their rows or images.
def test_admin_request_seeds_are_idempotent(admin_environment):
    _, database_path = admin_environment

    initialize_database(database_path)
    initialize_database(database_path)

    with sqlite3.connect(database_path) as connection:
        requests_count = connection.execute(
            """
            SELECT COUNT(*) FROM Court_Request
            WHERE CourtName LIKE 'SmashGo Demo Court Request %'
            """
        ).fetchone()[0]
        images_count = connection.execute(
            """
            SELECT COUNT(*) FROM Court_Request_Image
            JOIN Court_Request USING (RequestID)
            WHERE CourtName LIKE 'SmashGo Demo Court Request %'
            """
        ).fetchone()[0]
    assert requests_count == 2
    assert images_count == 2


# Task #94: Verify seeded requests include the fields Admin needs to make a decision.
def test_seeded_request_details_are_complete(admin_environment):
    client, _ = admin_environment
    login(client, DEMO_ADMIN)

    response = client.get("/api/admin/court-requests")

    assert response.status_code == 200
    for request_data in response.get_json():
        assert request_data["requestType"] == "CREATE"
        assert request_data["courtName"]
        assert request_data["location"]
        assert request_data["openTime"] < request_data["closeTime"]
        assert request_data["pricePerHour"] > 0
