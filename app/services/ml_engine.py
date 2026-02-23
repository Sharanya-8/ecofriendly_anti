"""
ML Engine — loads models once and exposes prediction functions.
"""
import os
import joblib
import pandas as pd
from flask import current_app

_soil_model = None
_crop_model = None
_crop_encoder = None
_soil_accuracy = None
_crop_accuracy = None

# ── Crop Knowledge Base ────────────────────────────────────────────────────────

CROP_DURATION = {
    "rice": 120, "wheat": 110, "maize": 100,
    "cotton": 160, "potato": 90, "sugarcane": 300,
    "soybean": 100, "groundnut": 110, "chickpea": 100,
    "mango": 365, "tomato": 90, "onion": 120,
    "banana": 270, "mustard": 100, "barley": 90,
    "lentil": 100, "orange": 365, "apple": 365,
    "grapes": 365, "watermelon": 80, "muskmelon": 85,
    "papaya": 240, "pomegranate": 365, "jute": 120,
    "coffee": 365, "coconut": 365, "blackgram": 75,
    "motherbeans": 90, "pigeonpeas": 130, "kidneybeans": 90,
}
DEFAULT_DURATION = 100

CROP_WATER_NEEDS = {
    "rice": 6, "wheat": 4, "maize": 5, "cotton": 5,
    "potato": 4, "mango": 2, "sugarcane": 7,
    "soybean": 4, "groundnut": 4, "chickpea": 3,
}
DEFAULT_WATER_NEED = 4


def _load_models():
    """Lazy-load ML models from the configured models directory."""
    global _soil_model, _crop_model, _crop_encoder, _soil_accuracy, _crop_accuracy
    if _soil_model is not None:
        return                               # already loaded
    model_dir = current_app.config["MODEL_DIR"]
    _soil_model = joblib.load(os.path.join(model_dir, "soil_model.pkl"))
    _soil_accuracy = joblib.load(os.path.join(model_dir, "soil_accuracy.pkl"))
    _crop_model = joblib.load(os.path.join(model_dir, "crop_model.pkl"))
    _crop_encoder = joblib.load(os.path.join(model_dir, "crop_label_encoder.pkl"))
    _crop_accuracy = joblib.load(os.path.join(model_dir, "crop_accuracy.pkl"))


def get_model_accuracies() -> dict:
    """Return model accuracy values for display."""
    _load_models()
    return {
        "soil": round(float(_soil_accuracy) * 100, 2),
        "crop": round(float(_crop_accuracy) * 100, 2),
    }


def predict_soil_fertility(N: float, P: float, K: float, ph: float, moisture: float) -> str:
    """Return soil fertility label predicted by the soil model."""
    _load_models()
    features = pd.DataFrame(
        [[N, P, K, ph, moisture]],
        columns=["N", "P", "K", "ph", "moisture"],
    )
    return str(_soil_model.predict(features)[0])


def predict_crop(
    N: float, P: float, K: float, ph: float,
    temperature: float, humidity: float, rainfall: float,
) -> str:
    """Return recommended crop name (lowercase)."""
    _load_models()
    features = pd.DataFrame(
        [[N, P, K, ph, temperature, humidity, rainfall]],
        columns=["N", "P", "K", "ph", "temperature", "humidity", "rainfall"],
    )
    encoded = _crop_model.predict(features)[0]
    return str(_crop_encoder.inverse_transform([encoded])[0]).lower()


def get_all_crop_names() -> list:
    """Return sorted list of all crop names the model knows."""
    _load_models()
    return sorted([c.lower() for c in _crop_encoder.classes_])


def get_crop_duration(crop_name: str) -> int:
    """Return growth duration in days for a crop (or default)."""
    return CROP_DURATION.get(crop_name.strip().lower(), DEFAULT_DURATION)


def get_water_need(crop_name: str) -> float:
    """Return base daily water need in litres/plant."""
    return CROP_WATER_NEEDS.get(crop_name.strip().lower(), DEFAULT_WATER_NEED)


def detect_season(month: int) -> str:
    """Return the farming season for a given month number."""
    if month in [6, 7, 8, 9]:
        return "Monsoon"
    elif month in [10, 11, 12, 1]:
        return "Winter"
    else:
        return "Summer"


def soil_nature_from_texture(sand: float, clay: float) -> str:
    """Return soil texture description."""
    if sand > 60:
        return "Sandy"
    elif clay > 40:
        return "Clayey"
    else:
        return "Loamy"
