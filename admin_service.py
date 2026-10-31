from contextlib import closing
from pathlib import Path
from typing import Any

import clock
from booking_service import BookingError
from database import get_db_connection

# Task #94: Centralize Admin status values used by request validation and booking conflicts.
ADMIN_COURT_STATUSES = ("ACTIVE", "DISABLED", "MAINTENANCE")
COURT_REQUEST_STATUSES = ("PENDING", "APPROVED", "REJECTED")
OCCUPYING_BOOKING_STATUSES = ("PENDING", "CONFIRMED", "CHECKED_IN")


# Task #94: Return every court, including disabled and maintenance courts, for the Admin view.
def list_admin_courts(database_path: str | Path) -> list[dict[str, Any]]:
    now = clock.now().strftime("%Y-%m-%d %H:%M")
    with closing(get_db_connection(database_path)) as connection:
        courts = connection.execute(
            """
            SELECT Court.CourtID, Court.CourtName, Court.Location,
                   Court.Description, Court.PricePerHour, Court.OpenTime,
                   Court.CloseTime, Court.Status, Court.ManagerID,
                   Users.FullName AS ManagerName,
                   (
                       SELECT COUNT(*)
                       FROM Booking
                       WHERE Booking.CourtID = Court.CourtID
                         AND Booking.Status IN (?, ?, ?)
                         AND Booking.BookingDate || ' ' || Booking.StartTime > ?
                         AND (
                             Booking.Status != 'PENDING'
                             OR Booking.HoldExpiresAt > ?
                         )
                   ) AS UpcomingBookings
            FROM Court
            JOIN Users ON Users.UserID = Court.ManagerID
            ORDER BY Court.CourtID
            """,
            (*OCCUPYING_BOOKING_STATUSES, now, now),
        ).fetchall()
        result = []
        for court in courts:
            images = connection.execute(
                """
                SELECT Url, SortOrder
                FROM Court_Image
                WHERE CourtID = ?
                ORDER BY SortOrder, ImageID
                """,
                (court["CourtID"],),
            ).fetchall()
            result.append(
                {
                    "courtId": court["CourtID"],
                    "courtName": court["CourtName"],
                    "location": court["Location"],
                    "description": court["Description"],
                    "pricePerHour": court["PricePerHour"],
                    "openTime": court["OpenTime"],
                    "closeTime": court["CloseTime"],
                    "status": court["Status"],
                    "managerId": court["ManagerID"],
                    "managerName": court["ManagerName"],
                    "upcomingBookings": court["UpcomingBookings"],
                    "images": [
                        {"url": image["Url"], "sortOrder": image["SortOrder"]}
                        for image in images
                    ],
                }
            )
        return result


# Task #94: Filter review requests using a fixed set of supported statuses and include their images.
def list_court_requests(
    database_path: str | Path, status: str = "PENDING"
) -> list[dict[str, Any]]:
    clean_status = status.upper()
    if clean_status != "ALL" and clean_status not in COURT_REQUEST_STATUSES:
        raise BookingError("INVALID_STATUS_FILTER")

    parameters: tuple[Any, ...] = ()
    status_clause = ""
    if clean_status != "ALL":
        status_clause = "WHERE Court_Request.Status = ?"
        parameters = (clean_status,)

    with closing(get_db_connection(database_path)) as connection:
        requests = connection.execute(
            f"""
            SELECT Court_Request.RequestID, Court_Request.ManagerID,
                   Users.FullName AS ManagerName, Court_Request.RequestType,
                   Court_Request.CourtID, Court_Request.CourtName,
                   Court_Request.Location, Court_Request.Description,
                   Court_Request.PricePerHour, Court_Request.OpenTime,
                   Court_Request.CloseTime, Court_Request.Reason,
                   Court_Request.Status, Court_Request.RejectReason,
                   Court_Request.CreatedAt
            FROM Court_Request
            JOIN Users ON Users.UserID = Court_Request.ManagerID
            {status_clause}
            ORDER BY Court_Request.CreatedAt, Court_Request.RequestID
            """,
            parameters,
        ).fetchall()
        result = []
        for request_row in requests:
            images = connection.execute(
                """
                SELECT Url, SortOrder
                FROM Court_Request_Image
                WHERE RequestID = ?
                ORDER BY SortOrder, ImageID
                """,
                (request_row["RequestID"],),
            ).fetchall()
            result.append(
                {
                    "requestId": request_row["RequestID"],
                    "managerId": request_row["ManagerID"],
                    "managerName": request_row["ManagerName"],
                    "requestType": request_row["RequestType"],
                    "courtId": request_row["CourtID"],
                    "courtName": request_row["CourtName"],
                    "location": request_row["Location"],
                    "description": request_row["Description"],
                    "pricePerHour": request_row["PricePerHour"],
                    "openTime": request_row["OpenTime"],
                    "closeTime": request_row["CloseTime"],
                    "reason": request_row["Reason"],
                    "status": request_row["Status"],
                    "rejectReason": request_row["RejectReason"],
                    "createdAt": request_row["CreatedAt"],
                    "images": [
                        {"url": image["Url"], "sortOrder": image["SortOrder"]}
                        for image in images
                    ],
                }
            )
        return result


# Task #94: Atomically approve or reject a pending CREATE request and retain its review metadata.
def review_court_request(
    database_path: str | Path,
    request_id: int,
    admin_id: int,
    decision: str,
    reject_reason: str | None = None,
) -> dict[str, Any]:
    clean_decision = decision.upper() if isinstance(decision, str) else ""
    clean_reason = reject_reason.strip() if isinstance(reject_reason, str) else ""
    if clean_decision not in ("APPROVED", "REJECTED"):
        raise BookingError("INVALID_DECISION")
    if clean_decision == "REJECTED" and not clean_reason:
        raise BookingError("INVALID_DECISION")

    reviewed_at = clock.now().strftime("%Y-%m-%d %H:%M:%S")
    with closing(get_db_connection(database_path)) as connection:
        connection.isolation_level = None
        connection.execute("BEGIN IMMEDIATE")
        try:
            request_row = connection.execute(
                """
                SELECT RequestID, ManagerID, RequestType, CourtName, Location,
                       Description, PricePerHour, OpenTime, CloseTime
                FROM Court_Request
                WHERE RequestID = ?
                """,
                (request_id,),
            ).fetchone()
            if request_row is None:
                raise BookingError("REQUEST_NOT_FOUND")

            current_status = connection.execute(
                "SELECT Status FROM Court_Request WHERE RequestID = ?",
                (request_id,),
            ).fetchone()["Status"]
            if current_status != "PENDING":
                raise BookingError("REQUEST_ALREADY_REVIEWED")
            if clean_decision == "APPROVED" and request_row["RequestType"] != "CREATE":
                raise BookingError("REQUEST_TYPE_NOT_SUPPORTED")

            court_id = None
            if clean_decision == "APPROVED":
                cursor = connection.execute(
                    """
                    INSERT INTO Court (
                        ManagerID, CourtName, Location, Description, PricePerHour,
                        OpenTime, CloseTime, Status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, 'ACTIVE')
                    """,
                    (
                        request_row["ManagerID"],
                        request_row["CourtName"],
                        request_row["Location"],
                        request_row["Description"],
                        request_row["PricePerHour"],
                        request_row["OpenTime"],
                        request_row["CloseTime"],
                    ),
                )
                court_id = cursor.lastrowid
                connection.execute(
                    """
                    INSERT INTO Court_Image (CourtID, Url, SortOrder)
                    SELECT ?, Url, SortOrder
                    FROM Court_Request_Image
                    WHERE RequestID = ?
                    """,
                    (court_id, request_id),
                )

            update = connection.execute(
                """
                UPDATE Court_Request
                SET Status = ?, RejectReason = ?, ReviewedBy = ?, ReviewedAt = ?
                WHERE RequestID = ? AND Status = 'PENDING'
                """,
                (
                    clean_decision,
                    clean_reason if clean_decision == "REJECTED" else None,
                    admin_id,
                    reviewed_at,
                    request_id,
                ),
            )
            if update.rowcount != 1:
                raise BookingError("REQUEST_ALREADY_REVIEWED")

            if clean_decision == "REJECTED":
                connection.execute(
                    """
                    INSERT INTO Notification (UserID, Title, Message, Type)
                    VALUES (?, ?, ?, 'COURT_REQUEST_RESULT')
                    """,
                    (
                        request_row["ManagerID"],
                        "Yêu cầu thêm sân đã bị từ chối",
                        f"Yêu cầu thêm sân “{request_row['CourtName']}” bị từ chối: {clean_reason}",
                    ),
                )

            connection.commit()
        except Exception:
            connection.rollback()
            raise

    result = {
        "requestId": request_id,
        "status": clean_decision,
        "reviewedBy": admin_id,
        "reviewedAt": reviewed_at,
    }
    if court_id is not None:
        result["courtId"] = court_id
    return result


# Task #94: Update a court's admin-controlled status without allowing disabling a court with future bookings.
def set_court_status(
    database_path: str | Path, court_id: int, status: str
) -> dict[str, Any]:
    clean_status = status.upper() if isinstance(status, str) else ""
    if clean_status not in ADMIN_COURT_STATUSES:
        raise BookingError("INVALID_STATUS")

    now = clock.now().strftime("%Y-%m-%d %H:%M")
    with closing(get_db_connection(database_path)) as connection:
        connection.isolation_level = None
        connection.execute("BEGIN IMMEDIATE")
        try:
            court = connection.execute(
                "SELECT CourtID FROM Court WHERE CourtID = ?", (court_id,)
            ).fetchone()
            if court is None:
                raise BookingError("COURT_NOT_FOUND")

            if clean_status == "DISABLED":
                upcoming = connection.execute(
                    """
                    SELECT 1
                    FROM Booking
                    WHERE CourtID = ?
                      AND Status IN (?, ?, ?)
                      AND BookingDate || ' ' || StartTime > ?
                      AND (
                          Status != 'PENDING'
                          OR HoldExpiresAt > ?
                      )
                    LIMIT 1
                    """,
                    (court_id, *OCCUPYING_BOOKING_STATUSES, now, now),
                ).fetchone()
                if upcoming:
                    raise BookingError("COURT_HAS_UPCOMING_BOOKINGS")

            connection.execute(
                "UPDATE Court SET Status = ? WHERE CourtID = ?",
                (clean_status, court_id),
            )
            connection.commit()
        except Exception:
            connection.rollback()
            raise

    return {"courtId": court_id, "status": clean_status}
