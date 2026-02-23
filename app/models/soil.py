"""
Soil model — CRUD for the SoilRecords table.
"""
from app.database import query_db, execute_db


def add_soil_record(
    farmer_id: int,
    crop_id: int,
    N: float,
    P: float,
    K: float,
    ph: float,
    moisture: float,
    sand: float,
    clay: float,
    soil_fertility: str,
) -> int:
    """Insert a soil reading. Returns new row id."""
    return execute_db(
        """
        INSERT INTO SoilRecords
            (farmer_id, crop_id, N, P, K, ph, moisture, sand, clay, soil_fertility)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (farmer_id, crop_id, N, P, K, ph, moisture, sand, clay, soil_fertility),
    )


def get_latest_soil_for_crop(crop_id: int):
    """Return the most recent soil record for a crop."""
    return query_db(
        """
        SELECT * FROM SoilRecords
        WHERE crop_id = ?
        ORDER BY recorded_at DESC
        LIMIT 1
        """,
        (crop_id,),
        one=True,
    )


def get_soil_records_for_farmer(farmer_id: int):
    """Return all soil records for a farmer, newest first."""
    return query_db(
        """
        SELECT * FROM SoilRecords
        WHERE farmer_id = ?
        ORDER BY recorded_at DESC
        """,
        (farmer_id,),
    )