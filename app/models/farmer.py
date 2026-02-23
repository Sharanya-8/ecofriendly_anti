"""
Farmer model — CRUD for the Farmers table.
"""
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import query_db, execute_db


def create_farmer(username: str, password: str, full_name: str, location: str, phone: str = None, email: str = None) -> int:
    """Insert a new farmer. Returns new row id, or -1 if username taken."""
    existing = get_farmer_by_username(username)
    if existing:
        return -1

    password_hash = generate_password_hash(password)

    return execute_db(
        """
        INSERT INTO Farmers (username, password_hash, full_name, location, phone, email)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (username.strip().lower(), password_hash, full_name.strip(), location.strip(), phone, email),
    )


def get_farmer_by_username(username: str):
    """Return a farmer dict for the given username (case-insensitive)."""
    return query_db(
        "SELECT * FROM Farmers WHERE LOWER(username) = LOWER(?)",
        (username.strip(),),
        one=True,
    )


def get_farmer_by_id(farmer_id: int):
    """Return a farmer dict for the given ID."""
    return query_db(
        "SELECT * FROM Farmers WHERE id = ?",
        (farmer_id,),
        one=True,
    )


def verify_password(farmer, password: str) -> bool:
    """Return True if the provided password matches the stored hash."""
    if farmer is None:
        return False
    return check_password_hash(farmer["password_hash"], password)


def update_farmer_location(farmer_id: int, location: str):
    """Update the farmer's primary district/location."""
    execute_db(
        "UPDATE Farmers SET location = ? WHERE id = ?",
        (location.strip(), farmer_id),
    )


def update_last_login(farmer_id: int):
    """Update the last login timestamp."""
    execute_db(
        "UPDATE Farmers SET last_login = datetime('now','localtime') WHERE id = ?",
        (farmer_id,),
    )