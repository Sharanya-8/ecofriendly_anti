import sqlite3
import os
from flask import g
from contextlib import contextmanager

# 🔥 Absolute path to your real database
DB_PATH = r"C:\Users\Shara\OneDrive\Desktop\ecofriendly_anti\ecofriendly_anti\data\farming.db"


def get_db():
    """Get or create SQLite connection stored on Flask's g object."""
    if "db" not in g:
        # Ensure database folder exists
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    """Close DB connection at end of request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def query_db(query, args=(), one=False):
    """Execute SELECT query and return dict-like rows."""
    db = get_db()
    cur = db.execute(query, args)
    rows = cur.fetchall()
    cur.close()
    return (rows[0] if rows else None) if one else rows


def execute_db(query, args=()):
    """Execute INSERT / UPDATE / DELETE and commit."""
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    last_id = cur.lastrowid
    cur.close()
    return last_id


@contextmanager
def transaction():
    """Context manager for safe transactions."""
    db = get_db()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise


def init_app(app):
    """Register teardown with Flask app."""
    app.teardown_appcontext(close_db)