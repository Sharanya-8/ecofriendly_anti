"""
IrrigationHistory model — CRUD for the IrrigationHistory table.
"""
from app.database import query_db, execute_db


def add_irrigation_record(
    farmer_id: int,
    crop_id: int,
    city: str,
    stage: str,
    days_after_sowing: int,
    et0: float,
    kc: float,
    water_required: float,
    decision: str,
) -> int:
    """Insert an irrigation event and return new row id."""
    return execute_db(
        """
        INSERT INTO IrrigationHistory
            (farmer_id, crop_id, city, stage, days_after_sowing, et0, kc, water_required, decision)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            farmer_id,
            crop_id,
            city,
            stage,
            days_after_sowing,
            round(et0, 3),
            round(kc, 3),
            round(water_required, 3),
            decision,
        ),
    )


def get_history_for_farmer(farmer_id: int, limit: int = 50):
    """Return all irrigation events for a farmer, newest first."""
    return query_db(
        """
        SELECT ih.*, c.crop_name, c.field_name
        FROM IrrigationHistory ih
        JOIN Crops c ON c.id = ih.crop_id
        WHERE ih.farmer_id = ?
        ORDER BY ih.recorded_at DESC
        LIMIT ?
        """,
        (farmer_id, limit),
    )


def get_history_for_crop(crop_id: int, limit: int = 20):
    """Return irrigation events for a specific crop, newest first."""
    return query_db(
        """
        SELECT * FROM IrrigationHistory
        WHERE crop_id = ?
        ORDER BY recorded_at DESC
        LIMIT ?
        """,
        (crop_id, limit),
    )


def get_last_irrigation_date(crop_id: int):
    """Get the date of last irrigation for a crop."""
    result = query_db(
        """
        SELECT DATE(recorded_at) as last_date
        FROM IrrigationHistory
        WHERE crop_id = ?
        ORDER BY recorded_at DESC
        LIMIT 1
        """,
        (crop_id,),
        one=True,
    )
    return result["last_date"] if result else None


def get_total_water_saved(farmer_id: int) -> float:
    """Return total water saved (0 water events) for dashboard metric."""
    result = query_db(
        """
        SELECT COALESCE(SUM(CASE WHEN water_required = 0 THEN 1 ELSE 0 END), 0) AS saved_events
        FROM IrrigationHistory
        WHERE farmer_id = ?
        """,
        (farmer_id,),
        one=True,
    )
    return result["saved_events"] if result else 0