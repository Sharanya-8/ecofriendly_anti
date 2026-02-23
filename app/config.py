import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class Config:
    # ── Security ──────────────────────────────────────────────────────────────
    SECRET_KEY = os.environ.get("SECRET_KEY", "eco_farming_secret_key_2024_change_in_prod")

    # ── MySQL Database ────────────────────────────────────────────────────────
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = int(os.environ.get("DB_PORT", 3399))
    DB_NAME = os.environ.get("DB_NAME", "smart_farm")
    DB_USER = os.environ.get("DB_USER", "farm_use")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "farming_secure_password_2024")

    # ── ML Models ─────────────────────────────────────────────────────────────
    MODEL_DIR = os.path.join(BASE_DIR, "models")

    # ── Weather API ───────────────────────────────────────────────────────────
    WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY", "565cec5804b4568a5ff6beb")
    WEATHER_BASE_URL = os.environ.get("WEATHER_BASE_URL", "https://api.openweathermap.org/data/2.5")

    # ── Pagination ────────────────────────────────────────────────────────────
    HISTORY_PER_PAGE = 10

    # ── Irrigation Scheduling ─────────────────────────────────────────────────
    SCHEDULE_DAYS = 30  # Generate 30-day irrigation schedule
