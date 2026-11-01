from contextlib import closing
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import clock
from booking_service import BookingError, OCCUPYING_STATUSES, parse_minutes
from database import get_db_connection


# Task #95: Validate public search filters before using them in court queries.
def validate_court_filters(
    booking_date: str, start_time: str, end_time: str
) -> tuple[date | None, int | None, int | None]:
    if not booking_date and not start_time and not end_time:
        return None, None, None
    if not booking_date or not start_time or not end_time:
        raise BookingError("INVALID_COURT_FILTER")

    try:
        clean_date = date.fromisoformat(booking_date)
    except (TypeError, ValueError):
        raise BookingError("INVALID_COURT_FILTER") from None

    start_minutes = parse_minutes(start_time)
    end_minutes = parse_minutes(end_time)
    if (
        start_minutes is None
        or end_minutes is None
        or start_minutes % 30
        or end_minutes % 30
        or end_minutes - start_minutes < 60
    ):
        raise BookingError("INVALID_COURT_FILTER")
    return clean_date, start_minutes, end_minutes


# Task #95: List active courts with optional location and real-time date/time availability filters.
def list_active_courts(
    database_path: str | Path,
    booking_date: str = "",
    start_time: str = "",
    end_time: str = "",
    location: str = "",
) -> list[Any]:
    clean_date, start_minutes, end_minutes = validate_court_filters(
        booking_date, start_time, end_time
    )
    conditions = ["Court.Status = 'ACTIVE'"]
    parameters: list[Any] = []

    clean_location = location.strip()
    if clean_location:
        escaped_location = (
            clean_location.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        )
        conditions.append(
            "(Court.Location LIKE ? ESCAPE '\\' OR Court.CourtName LIKE ? ESCAPE '\\')"
        )
        location_pattern = f"%{escaped_location}%"
        parameters.extend((location_pattern, location_pattern))

    if clean_date is not None:
        now = clock.now()
        requested_start = datetime.combine(clean_date, datetime.min.time()) + timedelta(
            minutes=start_minutes
        )
        if requested_start <= now:
            return []

        requested_start_time = f"{start_minutes // 60:02d}:{start_minutes % 60:02d}"
        requested_end_time = f"{end_minutes // 60:02d}:{end_minutes % 60:02d}"
        if end_minutes == 1440:
            requested_end_time = "24:00"
        now_text = now.strftime("%Y-%m-%d %H:%M")
        conditions.extend(
            (
                "Court.OpenTime <= ?",
                "Court.CloseTime >= ?",
                """
                NOT EXISTS (
                    SELECT 1 FROM Booking
                    WHERE Booking.CourtID = Court.CourtID
                      AND Booking.BookingDate = ?
                      AND Booking.Status IN (?, ?, ?)
                      AND Booking.StartTime < ?
                      AND Booking.EndTime > ?
                      AND (
                          Booking.Status != 'PENDING'
                          OR Booking.HoldExpiresAt > ?
                      )
                )
                """,
                """
                NOT EXISTS (
                    SELECT 1 FROM Court_Block
                    WHERE Court_Block.CourtID = Court.CourtID
                      AND Court_Block.BlockDate = ?
                      AND Court_Block.StartTime < ?
                      AND Court_Block.EndTime > ?
                )
                """,
            )
        )
        parameters.extend(
            (
                requested_start_time,
                requested_end_time,
                clean_date.isoformat(),
                *OCCUPYING_STATUSES,
                requested_end_time,
                requested_start_time,
                now_text,
                clean_date.isoformat(),
                requested_end_time,
                requested_start_time,
            )
        )

    with closing(get_db_connection(database_path)) as connection:
        return connection.execute(
            f"""
            SELECT Court.CourtID, Court.CourtName, Court.Location,
                   Court.Description, Court.PricePerHour, Court.OpenTime,
                   Court.CloseTime,
                   (
                       SELECT Court_Image.Url
                       FROM Court_Image
                       WHERE Court_Image.CourtID = Court.CourtID
                       ORDER BY Court_Image.SortOrder, Court_Image.ImageID
                       LIMIT 1
                   ) AS ImageUrl
            FROM Court
            WHERE {" AND ".join(conditions)}
            ORDER BY Court.CourtID
            """,
            parameters,
        ).fetchall()


# Task #95: Fetch an active court and all its photos for the public detail screen.
def get_active_court(database_path: str | Path, court_id: int) -> dict[str, Any] | None:
    with closing(get_db_connection(database_path)) as connection:
        court = connection.execute(
            """
            SELECT CourtID, CourtName, Location, Description, PricePerHour,
                   OpenTime, CloseTime
            FROM Court
            WHERE CourtID = ? AND Status = 'ACTIVE'
            """,
            (court_id,),
        ).fetchone()
        if court is None:
            return None
        images = connection.execute(
            """
            SELECT Url, SortOrder
            FROM Court_Image
            WHERE CourtID = ?
            ORDER BY SortOrder, ImageID
            """,
            (court_id,),
        ).fetchall()
        return {
            "courtId": court["CourtID"],
            "courtName": court["CourtName"],
            "location": court["Location"],
            "description": court["Description"],
            "pricePerHour": court["PricePerHour"],
            "openTime": court["OpenTime"],
            "closeTime": court["CloseTime"],
            "images": [
                {"url": image["Url"], "sortOrder": image["SortOrder"]}
                for image in images
            ],
        }


# Task #95: Fetch ordered images for a batch of active courts for public list responses.
def get_court_images(
    database_path: str | Path, court_ids: list[int]
) -> dict[int, list[dict[str, Any]]]:
    if not court_ids:
        return {}
    placeholders = ", ".join("?" for _ in court_ids)
    with closing(get_db_connection(database_path)) as connection:
        rows = connection.execute(
            f"""
            SELECT CourtID, Url, SortOrder
            FROM Court_Image
            WHERE CourtID IN ({placeholders})
            ORDER BY CourtID, SortOrder, ImageID
            """,
            court_ids,
        ).fetchall()
    result: dict[int, list[dict[str, Any]]] = {court_id: [] for court_id in court_ids}
    for row in rows:
        result[row["CourtID"]].append(
            {"url": row["Url"], "sortOrder": row["SortOrder"]}
        )
    return result


# Task #95: Generate one-hour, half-hour-step availability slots for a court and requested date.
def get_court_availability(
    database_path: str | Path, court_id: int, booking_date: str
) -> dict[str, Any]:
    try:
        clean_date = date.fromisoformat(booking_date)
    except (TypeError, ValueError):
        raise BookingError("INVALID_AVAILABILITY_DATE") from None

    now = clock.now()
    now_text = now.strftime("%Y-%m-%d %H:%M")
    with closing(get_db_connection(database_path)) as connection:
        court = connection.execute(
            """
            SELECT CourtID, CourtName, OpenTime, CloseTime
            FROM Court
            WHERE CourtID = ? AND Status = 'ACTIVE'
            """,
            (court_id,),
        ).fetchone()
        if court is None:
            raise BookingError("COURT_NOT_FOUND")

        occupied_rows = connection.execute(
            """
            SELECT StartTime, EndTime, 'BOOKING' AS Source
            FROM Booking
            WHERE CourtID = ? AND BookingDate = ?
              AND Status IN (?, ?, ?)
              AND (Status != 'PENDING' OR HoldExpiresAt > ?)
            UNION ALL
            SELECT StartTime, EndTime, 'BLOCK' AS Source
            FROM Court_Block
            WHERE CourtID = ? AND BlockDate = ?
            ORDER BY StartTime
            """,
            (
                court_id,
                clean_date.isoformat(),
                *OCCUPYING_STATUSES,
                now_text,
                court_id,
                clean_date.isoformat(),
            ),
        ).fetchall()

    opening = parse_minutes(court["OpenTime"])
    closing_time = parse_minutes(court["CloseTime"])
    occupied = [
        (
            parse_minutes(row["StartTime"]),
            parse_minutes(row["EndTime"]),
            row["Source"],
        )
        for row in occupied_rows
    ]
    slots = []
    for start in range(opening, closing_time - 60 + 1, 30):
        end = start + 60
        overlapping = [
            interval
            for interval in occupied
            if start < interval[1] and interval[0] < end
        ]
        too_short_gap = any(
            0 < (start - taken_end if taken_end <= start else taken_start - end) < 60
            for taken_start, taken_end, source in occupied
            if source == "BOOKING"
        )
        starts_at = datetime.combine(clean_date, datetime.min.time()) + timedelta(
            minutes=start
        )
        if overlapping:
            status = "BOOKED"
        elif starts_at <= now or too_short_gap:
            status = "UNAVAILABLE"
        else:
            status = "AVAILABLE"
        slots.append(
            {
                "startTime": f"{start // 60:02d}:{start % 60:02d}",
                "endTime": f"{end // 60:02d}:{end % 60:02d}" if end < 1440 else "24:00",
                "status": status,
                "available": status == "AVAILABLE",
            }
        )

    return {
        "courtId": court["CourtID"],
        "courtName": court["CourtName"],
        "date": clean_date.isoformat(),
        "slots": slots,
    }
