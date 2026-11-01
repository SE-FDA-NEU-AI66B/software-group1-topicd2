from datetime import timedelta

import pytest
from support import (
    ADMIN,
    ADMIN_ID,
    COURT_A,
    COURT_B,
    FIXED_NOW,
    IN_TWO_DAYS,
    MANAGER,
    TOMORROW,
    USER,
    YESTERDAY,
    add_booking,
    add_court_request,
    execute,
    login,
    query,
)


# Task #94: Give the Admin two pending requests and one upcoming booking on court A.
@pytest.fixture
def admin_environment(client, database_path):
    add_booking(database_path, COURT_A, TOMORROW, "20:00", "22:00", "CONFIRMED")
    add_court_request(database_path, "Sân Mới Hoàng Mai", "https://example.com/hoang-mai.jpg")
    add_court_request(database_path, "Sân Mới Long Biên", "https://example.com/long-bien.jpg")
    return client, database_path


# Task #94: Confirm the Admin page uses its dedicated rendered template.
def test_admin_page_renders_court_management_workspace(admin_environment):
    client, _ = admin_environment
    login(client, ADMIN)

    response = client.get("/admin/courts")

    assert response.status_code == 200
    assert "Yêu cầu chờ duyệt" in response.get_data(as_text=True)
    assert "Tất cả sân" in response.get_data(as_text=True)


# TC-32: Approval creates an ACTIVE court for the submitting Manager and copies every image.
def test_tc32_approving_request_creates_court_for_manager_and_copies_images(
    admin_environment,
):
    client, database_path = admin_environment
    login(client, ADMIN)
    request_data = client.get("/api/admin/court-requests").get_json()[0]
    execute(
        database_path,
        """
        INSERT INTO Court_Request_Image (RequestID, Url, SortOrder)
        VALUES (?, ?, 1)
        """,
        (request_data["requestId"], "https://example.com/new-2.jpg"),
    )

    response = client.post(
        f"/api/admin/court-requests/{request_data['requestId']}/review",
        json={"decision": "APPROVED"},
    )

    assert response.status_code == 200
    result = response.get_json()
    assert result["status"] == "APPROVED"
    assert result["reviewedBy"] == ADMIN_ID
    assert result["courtId"]
    court = query(
        database_path,
        "SELECT ManagerID, CourtName, Status FROM Court WHERE CourtID = ?",
        (result["courtId"],),
    )[0]
    request_status = query(
        database_path,
        "SELECT Status, ReviewedBy FROM Court_Request WHERE RequestID = ?",
        (request_data["requestId"],),
    )[0]
    copied_images = query(
        database_path,
        "SELECT Url, SortOrder FROM Court_Image WHERE CourtID = ? ORDER BY SortOrder",
        (result["courtId"],),
    )
    assert court == (request_data["managerId"], request_data["courtName"], "ACTIVE")
    assert request_status == ("APPROVED", ADMIN_ID)
    assert copied_images == [
        (request_data["images"][0]["url"], 0),
        ("https://example.com/new-2.jpg", 1),
    ]


# TC-33: Rejecting without a reason fails; a reasoned rejection updates the request without creating a court.
def test_tc33_rejection_requires_reason_and_does_not_create_court(admin_environment):
    client, database_path = admin_environment
    login(client, ADMIN)
    request_id = client.get("/api/admin/court-requests").get_json()[0]["requestId"]
    courts_before = query(database_path, "SELECT COUNT(*) FROM Court")[0][0]

    missing_reason = client.post(
        f"/api/admin/court-requests/{request_id}/review",
        json={"decision": "REJECTED"},
    )
    pending_after_missing_reason = query(
        database_path,
        "SELECT Status FROM Court_Request WHERE RequestID = ?",
        (request_id,),
    )[0][0]
    rejected = client.post(
        f"/api/admin/court-requests/{request_id}/review",
        json={"decision": "REJECTED", "rejectReason": "Thông tin chưa đầy đủ"},
    )

    assert missing_reason.status_code == 400
    assert missing_reason.get_json()["code"] == "INVALID_DECISION"
    assert pending_after_missing_reason == "PENDING"
    assert rejected.status_code == 200
    assert rejected.get_json()["status"] == "REJECTED"
    assert query(
        database_path,
        "SELECT Status, RejectReason FROM Court_Request WHERE RequestID = ?",
        (request_id,),
    )[0] == ("REJECTED", "Thông tin chưa đầy đủ")
    assert query(database_path, "SELECT COUNT(*) FROM Court")[0][0] == courts_before
    notification = query(
        database_path,
        """
        SELECT Title, Message, Type FROM Notification
        WHERE UserID = (
            SELECT ManagerID FROM Court_Request WHERE RequestID = ?
        )
        ORDER BY NotificationID DESC LIMIT 1
        """,
        (request_id,),
    )[0]
    assert notification[2] == "COURT_REQUEST_RESULT"
    assert "Thông tin chưa đầy đủ" in notification[1]


# TC-34: A reviewed request cannot be approved or rejected a second time.
def test_tc34_reviewed_request_cannot_be_reviewed_again(admin_environment):
    client, database_path = admin_environment
    login(client, ADMIN)
    request_id = client.get("/api/admin/court-requests").get_json()[0]["requestId"]

    approved = client.post(
        f"/api/admin/court-requests/{request_id}/review",
        json={"decision": "APPROVED"},
    )
    court_count_after_approval = query(database_path, "SELECT COUNT(*) FROM Court")[0][0]
    repeated = client.post(
        f"/api/admin/court-requests/{request_id}/review",
        json={"decision": "REJECTED", "rejectReason": "Đã xử lý"},
    )

    assert approved.status_code == 200
    assert repeated.status_code == 409
    assert repeated.get_json()["code"] == "REQUEST_ALREADY_REVIEWED"
    assert (
        query(database_path, "SELECT COUNT(*) FROM Court")[0][0]
        == court_count_after_approval
    )


# TC-35: Invalid decisions and missing requests have the documented errors; review requires Admin.
def test_tc35_review_rejects_invalid_input_missing_request_and_non_admins(
    client,
):
    login(client, ADMIN)

    invalid = client.post(
        "/api/admin/court-requests/1/review",
        json={"decision": "MAYBE"},
    )
    missing = client.post(
        "/api/admin/court-requests/9999/review",
        json={"decision": "APPROVED"},
    )

    assert invalid.status_code == 400
    assert invalid.get_json()["code"] == "INVALID_DECISION"
    assert missing.status_code == 404
    assert missing.get_json()["code"] == "REQUEST_NOT_FOUND"

    for account, expected_status, expected_code in (
        (None, 401, "UNAUTHENTICATED"),
        (USER, 403, "ADMIN_REQUIRED"),
        (MANAGER, 403, "ADMIN_REQUIRED"),
    ):
        role_client = client.application.test_client()
        if account:
            login(role_client, account)
        response = role_client.post(
            "/api/admin/court-requests/1/review",
            json={"decision": "APPROVED"},
        )
        assert response.status_code == expected_status
        assert response.get_json()["code"] == expected_code

# TC-36: The request list defaults to PENDING and rejects an unknown status filter.
def test_tc36_request_list_defaults_to_pending_and_validates_filter(admin_environment):
    client, _ = admin_environment
    login(client, ADMIN)
    request_id = client.get("/api/admin/court-requests").get_json()[0]["requestId"]
    assert client.post(
        f"/api/admin/court-requests/{request_id}/review",
        json={"decision": "REJECTED", "rejectReason": "Thiếu thông tin"},
    ).status_code == 200

    response = client.get("/api/admin/court-requests")
    invalid_response = client.get("/api/admin/court-requests?status=anything")

    assert response.status_code == 200
    assert len(response.get_json()) == 1
    assert all(item["status"] == "PENDING" for item in response.get_json())
    pending = response.get_json()[0]
    assert pending["images"][0]["url"].startswith("https://")
    assert pending["requestType"] == "CREATE"
    assert pending["courtName"]
    assert pending["location"]
    assert pending["openTime"] < pending["closeTime"]
    assert pending["pricePerHour"] > 0

    all_requests = client.get("/api/admin/court-requests?status=ALL")
    assert all_requests.status_code == 200
    assert {item["status"] for item in all_requests.get_json()} == {
        "PENDING",
        "REJECTED",
    }
    assert invalid_response.status_code == 400
    assert invalid_response.get_json()["code"] == "INVALID_STATUS_FILTER"


# TC-28: An upcoming confirmed booking blocks disabling; the court remains visible and the Admin list reports it.
def test_tc28_upcoming_booking_blocks_disable_and_remains_visible(admin_environment):
    client, database_path = admin_environment
    login(client, ADMIN)

    response = client.patch(f"/api/admin/courts/{COURT_A}/status", json={"status": "DISABLED"})

    assert response.status_code == 409
    assert response.get_json()["code"] == "COURT_HAS_UPCOMING_BOOKINGS"
    assert query(
        database_path, "SELECT Status FROM Court WHERE CourtID = ?", (COURT_A,)
    )[0][0] == "ACTIVE"

    admin_courts = client.get("/api/admin/courts")
    court_a = next(
        court for court in admin_courts.get_json() if court["courtId"] == COURT_A
    )
    assert court_a["upcomingBookings"] == 1
    assert court_a["images"][0]["url"].startswith("https://")
    assert "Sân Cầu Giấy A" in client.get("/courts").get_data(as_text=True)


# TC-27: Disabling hides a court from /courts and booking; reactivating makes it public again.
def test_tc27_admin_can_disable_and_reactivate_court(client, database_path):
    admin_client = client
    user_client = client.application.test_client()
    login(admin_client, ADMIN)

    disabled = admin_client.patch(
        f"/api/admin/courts/{COURT_B}/status", json={"status": "DISABLED"}
    )
    disabled_listing = admin_client.get("/courts").get_data(as_text=True)
    login(user_client, USER)
    booking = user_client.post(
        "/api/bookings",
        json={
            "courtId": COURT_B,
            "bookingDate": IN_TWO_DAYS,
            "startTime": "08:00",
            "endTime": "10:00",
        },
    )
    login(admin_client, ADMIN)
    active = admin_client.patch(
        f"/api/admin/courts/{COURT_B}/status", json={"status": "ACTIVE"}
    )
    active_listing = admin_client.get("/courts").get_data(as_text=True)

    assert disabled.status_code == 200
    assert disabled.get_json() == {"courtId": COURT_B, "status": "DISABLED"}
    assert "Sân Đống Đa B" not in disabled_listing
    assert booking.status_code == 404
    assert booking.get_json()["code"] == "COURT_NOT_FOUND"
    assert active.status_code == 200
    assert active.get_json() == {"courtId": COURT_B, "status": "ACTIVE"}
    assert "Sân Đống Đa B" in active_listing
    assert query(
        database_path, "SELECT Status FROM Court WHERE CourtID = ?", (COURT_B,)
    )[0][0] == "ACTIVE"


# TC-29: Cancelled, expired, and past bookings do not prevent disabling a court.
@pytest.mark.parametrize(
    ("status", "booking_date"),
    [
        ("CANCELLED", TOMORROW),
        ("EXPIRED", TOMORROW),
        ("CONFIRMED", YESTERDAY),
    ],
    ids=["cancelled-upcoming", "expired-upcoming", "confirmed-in-past"],
)
def test_tc29_non_upcoming_bookings_do_not_block_disable(
    client, database_path, status, booking_date
):
    add_booking(database_path, COURT_B, booking_date, "20:00", "22:00", status)
    login(client, ADMIN)

    response = client.patch(f"/api/admin/courts/{COURT_B}/status", json={"status": "DISABLED"})

    assert response.status_code == 200
    assert response.get_json()["status"] == "DISABLED"


# TC-30: An unexpired pending hold blocks disabling, but an expired pending hold does not.
def test_tc30_pending_hold_expiry_controls_disable_conflict(client, database_path):
    add_booking(
        database_path,
        COURT_A,
        TOMORROW,
        "20:00",
        "22:00",
        "PENDING",
        hold_expires_at=(FIXED_NOW + timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S"),
    )
    add_booking(
        database_path,
        COURT_B,
        TOMORROW,
        "20:00",
        "22:00",
        "PENDING",
        hold_expires_at=(FIXED_NOW - timedelta(seconds=1)).strftime("%Y-%m-%d %H:%M:%S"),
    )
    login(client, ADMIN)

    blocked = client.patch(
        f"/api/admin/courts/{COURT_A}/status", json={"status": "DISABLED"}
    )
    allowed = client.patch(
        f"/api/admin/courts/{COURT_B}/status", json={"status": "DISABLED"}
    )

    assert blocked.status_code == 409
    assert blocked.get_json()["code"] == "COURT_HAS_UPCOMING_BOOKINGS"
    assert allowed.status_code == 200
    assert allowed.get_json()["status"] == "DISABLED"


# TC-31: Status validation, missing-court errors, and status-endpoint authorization are enforced.
def test_tc31_status_errors_and_admin_permissions(client):
    login(client, ADMIN)

    invalid = client.patch(
        f"/api/admin/courts/{COURT_B}/status", json={"status": "UNKNOWN"}
    )
    missing = client.patch("/api/admin/courts/9999/status", json={"status": "DISABLED"})

    assert invalid.status_code == 400
    assert invalid.get_json()["code"] == "INVALID_STATUS"
    assert missing.status_code == 404
    assert missing.get_json()["code"] == "COURT_NOT_FOUND"

    for account, expected_status, expected_code in (
        (None, 401, "UNAUTHENTICATED"),
        (USER, 403, "ADMIN_REQUIRED"),
        (MANAGER, 403, "ADMIN_REQUIRED"),
    ):
        role_client = client.application.test_client()
        if account:
            login(role_client, account)
        response = role_client.patch(
            f"/api/admin/courts/{COURT_B}/status", json={"status": "DISABLED"}
        )
        assert response.status_code == expected_status
        assert response.get_json()["code"] == expected_code
