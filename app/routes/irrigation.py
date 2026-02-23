"""
Irrigation routes — /irrigate/<crop_id>, /irrigate/<crop_id>/weekly, /history, /schedule
"""
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, g, jsonify,
)
from app.routes.auth import login_required
from app.models.crop import get_crops_by_farmer, get_crop_by_id_and_farmer
from app.models.irrigation import (
    add_irrigation_record, get_history_for_farmer, get_history_for_crop,
)
from app.models.soil import get_latest_soil_for_crop
from app.services.weather import get_weather, get_weather_forecast
from app.services.ml_engine import get_water_need
from app.services.irrigation_engine import (
    get_current_stage, calculate_irrigation, get_weekly_plan,
)
from app.services.advanced_scheduler import (
    generate_full_lifecycle_schedule,
    save_full_schedule_to_db,
    get_full_schedule_for_crop,
    mark_irrigation_done,
    detect_and_handle_missed_irrigations,
    recalculate_after_missed_irrigation,
    get_schedule_statistics,
)

irrigation_bp = Blueprint("irrigation", __name__, url_prefix="/irrigation")


# ── Irrigation Dashboard — select a crop ──────────────────────────────────────

@irrigation_bp.route("/")
@login_required
def dashboard():
    farmer = g.farmer
    crops = get_crops_by_farmer(farmer["id"], status="active")
    enriched = []
    for crop in crops:
        stage_info = get_current_stage(crop["planting_date"], crop["growth_duration"])
        latest_soil = get_latest_soil_for_crop(crop["id"])
        enriched.append({
            **dict(crop),
            **stage_info,
            "last_moisture": latest_soil["moisture"] if latest_soil else "N/A",
        })
    return render_template("irrigation/dashboard.html", crops=enriched)


# ── Irrigation Advice for a crop ───────────────────────────────────────────────

@irrigation_bp.route("/<int:crop_id>", methods=["GET", "POST"])
@login_required
def advice(crop_id):
    farmer = g.farmer
    crop = get_crop_by_id_and_farmer(crop_id, farmer["id"])
    if not crop:
        flash("Crop not found or access denied.", "danger")
        return redirect(url_for("irrigation.dashboard"))

    crop = dict(crop)
    stage_info = get_current_stage(crop["planting_date"], crop["growth_duration"])

    # Fetch weather for farmer's location
    weather = None
    weather_error = None
    city = farmer["location"]
    try:
        weather = get_weather(city)
    except Exception as e:
        weather_error = str(e)

    result = None
    entered_moisture = None
    
    # PART 1: Handle POST - User submitted irrigation calculation
    if request.method == "POST" and weather:
        try:
            # CRITICAL: Capture user-entered moisture - this is the value they just typed
            entered_moisture = float(request.form["soil_moisture"])
            soil_moisture = entered_moisture
        except (ValueError, KeyError):
            flash("Please enter a valid soil moisture value.", "danger")
            # Get latest irrigation for display even on error
            latest_irrigation_records = get_history_for_crop(crop_id, limit=1)
            latest_irrigation = latest_irrigation_records[0] if latest_irrigation_records else None
            
            # Get baseline moisture for display
            latest_soil = get_latest_soil_for_crop(crop_id)
            current_moisture = float(latest_soil["moisture"]) if latest_soil else 50.0
            
            return render_template(
                "irrigation/advice.html",
                crop=crop, 
                stage_info=stage_info,
                current_moisture=current_moisture,
                entered_moisture=None,
                latest_irrigation=latest_irrigation,
                weather=weather,
                weather_error=weather_error, 
                result=None,
            )

        # Calculate irrigation recommendation using entered moisture
        result = calculate_irrigation(
            temperature=weather["temp"],
            rainfall=weather["rain"],
            kc=stage_info["kc"],
            soil_moisture=soil_moisture,
        )

        # Save to history
        add_irrigation_record(
            farmer_id=farmer["id"],
            crop_id=crop_id,
            city=city,
            stage=stage_info["stage_name"],
            days_after_sowing=stage_info["days_after_sowing"],
            et0=result["et0"],
            kc=stage_info["kc"],
            water_required=result["net_water"],
            decision=result["decision"],
        )
        
        # CRITICAL: Immediately fetch the latest irrigation record after saving
        # This ensures UI shows the just-saved record
        latest_irrigation_records = get_history_for_crop(crop_id, limit=1)
        latest_irrigation = latest_irrigation_records[0] if latest_irrigation_records else None
        
        # Get baseline moisture (for reference display)
        latest_soil = get_latest_soil_for_crop(crop_id)
        current_moisture = float(latest_soil["moisture"]) if latest_soil else 50.0
        
        flash("Irrigation record saved successfully!", "success")
        
        # Return with all updated data
        return render_template(
            "irrigation/advice.html",
            crop=crop,
            stage_info=stage_info,
            current_moisture=current_moisture,
            entered_moisture=entered_moisture,  # Show the value user just entered
            latest_irrigation=latest_irrigation,  # Show the just-saved record
            weather=weather,
            weather_error=weather_error,
            result=result,
        )
    
    # PART 2: Handle GET - Initial page load or refresh
    # Get latest irrigation record
    latest_irrigation_records = get_history_for_crop(crop_id, limit=1)
    latest_irrigation = latest_irrigation_records[0] if latest_irrigation_records else None

    # Determine baseline soil moisture for display
    # Priority: 1. Latest soil reading, 2. Default
    latest_soil = get_latest_soil_for_crop(crop_id)
    current_moisture = float(latest_soil["moisture"]) if latest_soil else 50.0

    return render_template(
        "irrigation/advice.html",
        crop=crop,
        stage_info=stage_info,
        current_moisture=current_moisture,
        entered_moisture=None,  # No entered value on GET
        latest_irrigation=latest_irrigation,
        weather=weather,
        weather_error=weather_error,
        result=None,
    )


# ── Weekly 5-day Irrigation Plan ───────────────────────────────────────────────

@irrigation_bp.route("/<int:crop_id>/weekly")
@login_required
def weekly(crop_id):
    farmer = g.farmer
    crop = get_crop_by_id_and_farmer(crop_id, farmer["id"])
    if not crop:
        flash("Crop not found.", "danger")
        return redirect(url_for("irrigation.dashboard"))

    crop = dict(crop)
    stage_info = get_current_stage(crop["planting_date"], crop["growth_duration"])
    latest_soil = get_latest_soil_for_crop(crop_id)
    soil_moisture = latest_soil["moisture"] if latest_soil else 50.0
    base_water = get_water_need(crop["crop_name"])

    forecast = []
    weekly_plan = []
    total_saved = 0.0
    forecast_error = None

    try:
        forecast = get_weather_forecast(farmer["location"])
        weekly_plan = get_weekly_plan(forecast, base_water, soil_moisture)
        total_saved = sum(d["saved"] for d in weekly_plan)
    except Exception as e:
        forecast_error = str(e)

    return render_template(
        "irrigation/weekly.html",
        crop=crop,
        stage_info=stage_info,
        weekly_plan=weekly_plan,
        total_saved=round(total_saved, 2),
        forecast_error=forecast_error,
        soil_moisture=soil_moisture,
    )


# ── Irrigation History ─────────────────────────────────────────────────────────

@irrigation_bp.route("/history")
@login_required
def history():
    farmer = g.farmer
    records = get_history_for_farmer(farmer["id"], limit=100)
    return render_template("irrigation/history.html", records=records)



# ── Full Lifecycle Schedule ────────────────────────────────────────────────────

@irrigation_bp.route("/<int:crop_id>/schedule")
@login_required
def full_schedule(crop_id):
    """Display complete irrigation schedule from planting to harvest."""
    farmer = g.farmer
    crop = get_crop_by_id_and_farmer(crop_id, farmer["id"])
    
    if not crop:
        flash("Crop not found or access denied.", "danger")
        return redirect(url_for("irrigation.dashboard"))
    
    crop = dict(crop)
    
    # Get or generate schedule
    schedule = get_full_schedule_for_crop(crop_id)
    
    if not schedule:
        # Generate initial schedule using latest soil reading
        latest_soil = get_latest_soil_for_crop(crop_id)
        initial_moisture = float(latest_soil["moisture"]) if latest_soil else 60.0
        
        new_schedule = generate_full_lifecycle_schedule(
            farmer_id=farmer["id"],
            crop_id=crop_id,
            crop_name=crop["crop_name"],
            planting_date=crop["planting_date"],
            growth_duration=crop["growth_duration"],
            initial_soil_moisture=initial_moisture,
            city=farmer["location"],
        )
        
        save_full_schedule_to_db(farmer["id"], crop_id, new_schedule)
        schedule = get_full_schedule_for_crop(crop_id)
        flash("Irrigation schedule generated successfully!", "success")
    
    # Check for missed irrigations
    missed_count = detect_and_handle_missed_irrigations(crop_id)
    if missed_count > 0:
        flash(f"Warning: {missed_count} irrigation(s) were missed. Consider recalculating schedule.", "warning")
    
    # Get statistics
    stats = get_schedule_statistics(crop_id)
    
    # Get current stage
    stage_info = get_current_stage(crop["planting_date"], crop["growth_duration"])
    
    # Get latest soil moisture for display
    latest_soil = get_latest_soil_for_crop(crop_id)
    current_moisture = float(latest_soil["moisture"]) if latest_soil else None
    
    return render_template(
        "irrigation/schedule.html",
        crop=crop,
        schedule=schedule,
        stats=stats,
        stage_info=stage_info,
        missed_count=missed_count,
        current_moisture=current_moisture,
    )


@irrigation_bp.route("/<int:crop_id>/schedule/generate", methods=["POST"])
@login_required
def generate_schedule(crop_id):
    """Generate or regenerate full irrigation schedule with optional soil moisture input."""
    farmer = g.farmer
    crop = get_crop_by_id_and_farmer(crop_id, farmer["id"])
    
    if not crop:
        flash("Crop not found or access denied.", "danger")
        return redirect(url_for("irrigation.dashboard"))
    
    crop = dict(crop)
    
    # CRITICAL FIX: Use user-provided soil moisture if available
    # This ensures we ALWAYS use the latest value, not cached/old values
    user_moisture = request.form.get("soil_moisture", type=float)
    
    if user_moisture is not None:
        # User explicitly provided soil moisture - USE IT!
        initial_moisture = user_moisture
        flash(f"Schedule generated using current soil moisture: {initial_moisture}%", "info")
    else:
        # Fallback to latest soil reading only if user didn't provide
        latest_soil = get_latest_soil_for_crop(crop_id)
        initial_moisture = float(latest_soil["moisture"]) if latest_soil else 60.0
        flash(f"Schedule generated using stored soil moisture: {initial_moisture}%", "info")
    
    # Generate schedule with the correct moisture value
    schedule = generate_full_lifecycle_schedule(
        farmer_id=farmer["id"],
        crop_id=crop_id,
        crop_name=crop["crop_name"],
        planting_date=crop["planting_date"],
        growth_duration=crop["growth_duration"],
        initial_soil_moisture=initial_moisture,  # Use the correct value!
        city=farmer["location"],
    )
    
    # Save to database
    save_full_schedule_to_db(farmer["id"], crop_id, schedule)
    
    flash(f"Generated {len(schedule)} irrigation events for {crop['crop_name'].title()}!", "success")
    return redirect(url_for("irrigation.full_schedule", crop_id=crop_id))


@irrigation_bp.route("/schedule/<int:schedule_id>/complete", methods=["POST"])
@login_required
def mark_complete(schedule_id):
    """Mark a scheduled irrigation as completed."""
    farmer = g.farmer
    
    # Verify ownership
    schedule = query_db(
        "SELECT * FROM IrrigationSchedule WHERE id = %s AND farmer_id = %s",
        (schedule_id, farmer["id"]),
        one=True
    )
    
    if not schedule:
        return jsonify({"success": False, "message": "Schedule not found"}), 404
    
    # Get actual water amount from form
    actual_water = request.form.get("actual_water", type=float)
    
    # Mark as done
    success = mark_irrigation_done(schedule_id, actual_water)
    
    if success:
        flash("Irrigation marked as completed!", "success")
        return redirect(url_for("irrigation.full_schedule", crop_id=schedule["crop_id"]))
    else:
        flash("Failed to mark irrigation as completed.", "danger")
        return redirect(url_for("irrigation.dashboard"))


@irrigation_bp.route("/<int:crop_id>/schedule/recalculate", methods=["POST"])
@login_required
def recalculate_schedule(crop_id):
    """Recalculate schedule after missed irrigations with optional soil moisture input."""
    farmer = g.farmer
    crop = get_crop_by_id_and_farmer(crop_id, farmer["id"])
    
    if not crop:
        flash("Crop not found or access denied.", "danger")
        return redirect(url_for("irrigation.dashboard"))
    
    crop = dict(crop)
    
    # CRITICAL FIX: Check if user provided current soil moisture
    user_moisture = request.form.get("soil_moisture", type=float)
    
    if user_moisture is not None:
        # User provided moisture - use it directly for recalculation
        # This overrides any estimated or stored values
        estimated_moisture = user_moisture
        flash(f"Recalculating with current soil moisture: {estimated_moisture}%", "info")
        
        # Detect missed irrigations
        missed_count = detect_and_handle_missed_irrigations(crop_id)
        
        # Regenerate schedule with user-provided moisture
        new_schedule = generate_full_lifecycle_schedule(
            farmer_id=farmer["id"],
            crop_id=crop_id,
            crop_name=crop["crop_name"],
            planting_date=crop["planting_date"],
            growth_duration=crop["growth_duration"],
            initial_soil_moisture=estimated_moisture,
            city=farmer["location"],
        )
        
        save_full_schedule_to_db(farmer["id"], crop_id, new_schedule)
        
        msg = f"Schedule recalculated with current moisture!"
        if missed_count > 0:
            msg += f" {missed_count} missed irrigation(s) detected."
        if estimated_moisture < 30:
            msg += " ⚠️ Urgent irrigation needed!"
        flash(msg, "info")
    else:
        # No user input - use automatic recalculation
        result = recalculate_after_missed_irrigation(
            farmer_id=farmer["id"],
            crop_id=crop_id,
            crop_name=crop["crop_name"],
            planting_date=crop["planting_date"],
            growth_duration=crop["growth_duration"],
            city=farmer["location"],
        )
        
        if result["recalculated"]:
            msg = f"Schedule recalculated! {result['missed_count']} missed irrigation(s) detected."
            if result["urgent_irrigation"]:
                msg += " ⚠️ Urgent irrigation needed!"
            flash(msg, "info")
        else:
            flash("No missed irrigations detected. Schedule is up to date.", "success")
    
    return redirect(url_for("irrigation.full_schedule", crop_id=crop_id))


# Import query_db for the mark_complete route
from app.database import query_db



# ── Live Location Weather API ──────────────────────────────────────────────────

@irrigation_bp.route("/weather/live", methods=["POST"])
@login_required
def get_live_weather():
    """Get weather data using live GPS coordinates."""
    try:
        data = request.get_json()
        lat = data.get("latitude")
        lon = data.get("longitude")
        
        if not lat or not lon:
            return jsonify({
                "success": False,
                "message": "Latitude and longitude are required"
            }), 400
        
        # Fetch weather using coordinates
        weather = get_weather(lat=float(lat), lon=float(lon))
        
        return jsonify({
            "success": True,
            "weather": weather
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500
