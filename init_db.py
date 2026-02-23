"""
init_db.py — Run this ONCE to create the SQLite database schema.
Usage: python init_db.py
"""
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "farming.db")

SCHEMA = """
-- ── Farmers ──────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS Farmers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    location TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    last_login DATETIME,
    created_at DATETIME DEFAULT (datetime('now','localtime'))
);

-- ── Crops ─────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS Crops (
    id              INTEGER  PRIMARY KEY AUTOINCREMENT,
    farmer_id       INTEGER  NOT NULL REFERENCES Farmers(id) ON DELETE CASCADE,
    crop_name       TEXT     NOT NULL,
    field_name      TEXT     NOT NULL DEFAULT 'My Field',
    planting_date   DATE     NOT NULL,
    growth_duration INTEGER  NOT NULL DEFAULT 100,
    status          TEXT     NOT NULL DEFAULT 'active'
                             CHECK(status IN ('active','harvested')),
    created_at      DATETIME NOT NULL DEFAULT (datetime('now','localtime'))
);

-- ── SoilRecords ───────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS SoilRecords (
    id             INTEGER  PRIMARY KEY AUTOINCREMENT,
    farmer_id      INTEGER  NOT NULL REFERENCES Farmers(id) ON DELETE CASCADE,
    crop_id        INTEGER  REFERENCES Crops(id) ON DELETE SET NULL,
    N              REAL     NOT NULL,
    P              REAL     NOT NULL,
    K              REAL     NOT NULL,
    ph             REAL     NOT NULL,
    moisture       REAL     NOT NULL,
    sand           REAL     NOT NULL DEFAULT 0,
    clay           REAL     NOT NULL DEFAULT 0,
    soil_fertility TEXT     NOT NULL DEFAULT '',
    recorded_at    DATETIME NOT NULL DEFAULT (datetime('now','localtime'))
);

-- ── IrrigationHistory ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS IrrigationHistory (
    id                INTEGER  PRIMARY KEY AUTOINCREMENT,
    farmer_id         INTEGER  NOT NULL REFERENCES Farmers(id) ON DELETE CASCADE,
    crop_id           INTEGER  REFERENCES Crops(id) ON DELETE SET NULL,
    city              TEXT     NOT NULL DEFAULT '',
    stage             TEXT     NOT NULL DEFAULT '',
    days_after_sowing INTEGER  NOT NULL DEFAULT 0,
    et0               REAL     NOT NULL DEFAULT 0.0,
    kc                REAL     NOT NULL DEFAULT 1.0,
    water_required    REAL     NOT NULL DEFAULT 0.0,
    decision          TEXT     NOT NULL DEFAULT '',
    recorded_at       DATETIME NOT NULL DEFAULT (datetime('now','localtime'))
);

-- ── Indexes ───────────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_crops_farmer    ON Crops(farmer_id);
CREATE INDEX IF NOT EXISTS idx_soil_farmer     ON SoilRecords(farmer_id);
CREATE INDEX IF NOT EXISTS idx_soil_crop       ON SoilRecords(crop_id);
CREATE INDEX IF NOT EXISTS idx_irr_farmer      ON IrrigationHistory(farmer_id);
CREATE INDEX IF NOT EXISTS idx_irr_crop        ON IrrigationHistory(crop_id);
"""


def main():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()
    print(f"✅ Database initialised at: {DB_PATH}")
    print("   Tables created: Farmers, Crops, SoilRecords, IrrigationHistory")
    print("   Run 'python run.py' to start the application.")


if __name__ == "__main__":
    main()
