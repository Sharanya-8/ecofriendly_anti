"""
Main routes — /, /dashboard
"""
from flask import Blueprint, render_template, redirect, url_for, flash, g
from app.routes.auth import login_required
from app.models.crop import get_crops_by_farmer
from app.models.irrigation import get_history_for_farmer, get_total_water_saved
from app.services.weather import get_weather
from app.services.irrigation_engine import get_current_stage

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    if g.farmer:
        return redirect(url_for("main.dashboard"))
    return redirect(url_for("auth.login"))


@main_bp.route("/dashboard")
@login_required
def dashboard():
    farmer = g.farmer
    crops = get_crops_by_farmer(farmer["id"], status="active")

    # Enrich each crop with its current stage info
    enriched_crops = []
    for crop in crops:
        stage_info = get_current_stage(crop["planting_date"], crop["growth_duration"])
        enriched_crops.append({**dict(crop), **stage_info})

    # Recent irrigation events (last 5)
    recent_history = get_history_for_farmer(farmer["id"], limit=5)
    saved_events = get_total_water_saved(farmer["id"])

    # Weather for farmer's location
    weather = None
    weather_error = None
    try:
        weather = get_weather(farmer["location"])
    except Exception as e:
        weather_error = str(e)

    return render_template(
        "main/dashboard.html",
        farmer=farmer,
        crops=enriched_crops,
        recent_history=recent_history,
        saved_events=saved_events,
        weather=weather,
        weather_error=weather_error,
    )
