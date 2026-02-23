"""
Crop model — CRUD for the Crops table.
"""
from app.database import query_db, execute_db


def add_crop(
    farmer_id: int,
    crop_name: str,
    field_name: str,
    planting_date: str,
    growth_duration: int,
) -> int:
    """Insert a new crop record. Returns new row id."""
    return execute_db(
        """
        INSERT INTO Crops 
            (farmer_id, crop_name, field_name, planting_date, growth_duration, status)
        VALUES (?, ?, ?, ?, ?, 'active')
        """,
        (
            farmer_id,
            crop_name.strip().lower(),
            field_name.strip(),
            planting_date,
            int(growth_duration),
        ),
    )


def get_crops_by_farmer(farmer_id: int, status: str = None):
    """Return all crops for a farmer. Optionally filter by 'active'/'harvested'."""
    if status:
        return query_db(
            """
            SELECT * FROM Crops 
            WHERE farmer_id = ? AND status = ?
            ORDER BY planting_date DESC
            """,
            (farmer_id, status),
        )

    return query_db(
        """
        SELECT * FROM Crops 
        WHERE farmer_id = ?
        ORDER BY planting_date DESC
        """,
        (farmer_id,),
    )


def get_crop_by_id(crop_id: int):
    """Return a single crop dict."""
    return query_db(
        "SELECT * FROM Crops WHERE id = ?",
        (crop_id,),
        one=True,
    )


def get_crop_by_id_and_farmer(crop_id: int, farmer_id: int):
    """Return a crop only if it belongs to the given farmer (security check)."""
    return query_db(
        """
        SELECT * FROM Crops 
        WHERE id = ? AND farmer_id = ?
        """,
        (crop_id, farmer_id),
        one=True,
    )


def update_crop_status(crop_id: int, status: str):
    """Set crop status to 'active', 'harvested', or 'failed'."""
    execute_db(
        "UPDATE Crops SET status = ? WHERE id = ?",
        (status, crop_id),
    )


def delete_crop(crop_id: int, farmer_id: int):
    """Delete a crop (only if owned by farmer)."""
    execute_db(
        "DELETE FROM Crops WHERE id = ? AND farmer_id = ?",
        (crop_id, farmer_id),
    )


def get_active_crops_count(farmer_id: int) -> int:
    """Get count of active crops for a farmer."""
    result = query_db(
        """
        SELECT COUNT(*) as count 
        FROM Crops 
        WHERE farmer_id = ? AND status = 'active'
        """,
        (farmer_id,),
        one=True,
    )

    return result["count"] if result else 0