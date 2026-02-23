"""
IrrigationSchedule model — CRUD for the IrrigationSchedule table.
"""
from app.database import query_db, execute_db
from datetime import date, timedelta


def get_upcoming_schedule(farmer_id: int, days: int = 7):
    """Get upcoming irrigation schedule for next N days."""
    today = date.today()
    end_date = today + timedelta(days=days)

    return query_db(
        """
        SELECT s.*, c.crop_name, c.field_name
        FROM IrrigationSchedule s
        JOIN Crops c ON c.id = s.crop_id
        WHERE s.farmer_id = ?
          AND s.scheduled_date BETWEEN ? AND ?
          AND s.status IN ('pending', 'missed')
        ORDER BY s.scheduled_date, c.field_name
        """,
        (farmer_id, today, end_date),
    )


def get_schedule_by_crop(crop_id: int, limit: int = 30):
    """Get irrigation schedule for a specific crop."""
    return query_db(
        """
        SELECT * FROM IrrigationSchedule
        WHERE crop_id = ?
        ORDER BY scheduled_date ASC
        LIMIT ?
        """,
        (crop_id, limit),
    )


def mark_completed(schedule_id: int, actual_water: float = None):
    """Mark a schedule entry as completed."""
    if actual_water:
        execute_db(
            """
            UPDATE IrrigationSchedule
            SET status = 'completed',
                completed_at = datetime('now'),
                water_amount = ?
            WHERE id = ?
            """,
            (actual_water, schedule_id),
        )
    else:
        execute_db(
            """
            UPDATE IrrigationSchedule
            SET status = 'completed',
                completed_at = datetime('now')
            WHERE id = ?
            """,
            (schedule_id,),
        )


def mark_skipped(schedule_id: int, reason: str):
    """Mark a schedule entry as skipped with reason."""
    execute_db(
        """
        UPDATE IrrigationSchedule
        SET status = 'skipped',
            reason = ?
        WHERE id = ?
        """,
        (reason, schedule_id),
    )


def get_missed_count(farmer_id: int) -> int:
    """Get count of missed irrigations."""
    result = query_db(
        """
        SELECT COUNT(*) as count
        FROM IrrigationSchedule
        WHERE farmer_id = ? AND status = 'missed'
        """,
        (farmer_id,),
        one=True,
    )
    return result["count"] if result else 0


def clear_old_schedules(crop_id: int):
    """Delete old completed/skipped schedules older than 60 days."""
    cutoff_date = date.today() - timedelta(days=60)
    execute_db(
        """
        DELETE FROM IrrigationSchedule
        WHERE crop_id = ?
          AND scheduled_date < ?
          AND status IN ('completed', 'skipped')
        """,
        (crop_id, cutoff_date),
    )