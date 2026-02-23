"""
Crop routes — /recommend, /confirm, /my-crops, /delete-crop/<id>
"""
from datetime import date
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, session, g,
)
from app.routes.auth import login_required
from app.models.crop import (
    add_crop, get_crops_by_farmer,
    get_crop_by_id_and_farmer, update_crop_status, delete_crop,
)
from app.models.soil import add_soil_record
from app.services.weather import get_weather, DISTRICTS
from app.services.ml_engine import (
    predict_soil_fertility, predict_crop,
    get_crop_duration, detect_season, soil_nature_from_texture,
    get_model_accuracies, get_all_crop_names,
)
from app.services.irrigation_engine import get_current_stage

crops_bp = Blueprint("crops", __name__, url_prefix="/crops")


# ── My Crops list ──────────────────────────────────────────────────────────────

@crops_bp.route("/")
@login_required
def my_crops():
    farmer = g.farmer
    crops = get_crops_by_farmer(farmer["id"])
    enriched = []
    for crop in crops:
        stage_info = get_current_stage(crop["planting_date"], crop["growth_duration"])
        enriched.append({**dict(crop), **stage_info})
    return render_template("crops/my_crops.html", crops=enriched)


# ── Crop Recommendation ────────────────────────────────────────────────────────

@crops_bp.route("/recommend", methods=["GET", "POST"])
@login_required
def recommend():
    farmer = g.farmer
    accuracies = get_model_accuracies()
    districts = DISTRICTS

    if request.method == "POST":
        try:
            N        = float(request.form["N"])
            P        = float(request.form["P"])
            K        = float(request.form["K"])
            ph       = float(request.form["ph"])
            moisture = float(request.form["moisture"])
            sand     = float(request.form["sand"])
            clay     = float(request.form["clay"])
            city     = request.form["city"].strip()
            month    = int(request.form["month"])
            field_name = request.form.get("field_name", "My Field").strip()
        except (ValueError, KeyError):
            flash("Invalid input. Please fill all fields with numeric values.", "danger")
            return render_template("crops/recommend.html",
                                   accuracies=accuracies, districts=districts)

        # Validate ranges
        if not (0 <= ph <= 14):
            flash("pH must be between 0 and 14.", "danger")
            return render_template("crops/recommend.html",
                                   accuracies=accuracies, districts=districts)
        if not (1 <= month <= 12):
            flash("Month must be between 1 and 12.", "danger")
            return render_template("crops/recommend.html",
                                   accuracies=accuracies, districts=districts)

        # Fetch weather
        try:
            weather = get_weather(city)
        except Exception as e:
            flash(f"Weather API error: {e}", "danger")
            return render_template("crops/recommend.html",
                                   accuracies=accuracies, districts=districts)

        # ML predictions
        try:
            soil_fertility = predict_soil_fertility(N, P, K, ph, moisture)
            recommended_crop = predict_crop(
                N, P, K, ph,
                weather["temp"], weather["humidity"], weather["rain"],
            )
        except Exception as e:
            flash(f"Model prediction error: {e}", "danger")
            return render_template("crops/recommend.html",
                                   accuracies=accuracies, districts=districts)

        soil_nature = soil_nature_from_texture(sand, clay)
        season = detect_season(month)
        growth_duration = get_crop_duration(recommended_crop)

        # Store recommendation payload in session for confirm step
        session["recommendation"] = {
            "N": N, "P": P, "K": K, "ph": ph, "moisture": moisture,
            "sand": sand, "clay": clay,
            "city": city, "month": month, "field_name": field_name,
            "temperature": weather["temp"],
            "humidity": weather["humidity"],
            "rainfall": weather["rain"],
            "soil_fertility": soil_fertility,
            "soil_nature": soil_nature,
            "season": season,
            "recommended_crop": recommended_crop,
            "growth_duration": growth_duration,
        }

        return render_template(
            "crops/confirm.html",
            rec=session["recommendation"],
            weather=weather,
        )

    return render_template("crops/recommend.html",
                           accuracies=accuracies, districts=districts)


# ── Confirm & Store Crop ───────────────────────────────────────────────────────

@crops_bp.route("/confirm", methods=["POST"])
@login_required
def confirm():
    farmer = g.farmer
    rec = session.get("recommendation")

    if not rec:
        flash("No pending recommendation. Please run the recommendation again.", "warning")
        return redirect(url_for("crops.recommend"))

    # Validate planting date
    planting_date_str = request.form.get("planting_date", "")
    try:
        planting_date = date.fromisoformat(planting_date_str)
    except ValueError:
        flash("Invalid planting date. Use YYYY-MM-DD format.", "danger")
        return redirect(url_for("crops.recommend"))

    # Insert Crop
    crop_id = add_crop(
        farmer_id=farmer["id"],
        crop_name=rec["recommended_crop"],
        field_name=rec["field_name"],
        planting_date=str(planting_date),
        growth_duration=rec["growth_duration"],
    )

    # Insert SoilRecord linked to this crop
    add_soil_record(
        farmer_id=farmer["id"],
        crop_id=crop_id,
        N=rec["N"], P=rec["P"], K=rec["K"],
        ph=rec["ph"], moisture=rec["moisture"],
        sand=rec["sand"], clay=rec["clay"],
        soil_fertility=rec["soil_fertility"],
    )

    session.pop("recommendation", None)
    flash(
        f"🌱 {rec['recommended_crop'].title()} added to your farm! "
        "Head to irrigation when ready.",
        "success",
    )
    return redirect(url_for("crops.my_crops"))


# ── Mark Harvested ─────────────────────────────────────────────────────────────

@crops_bp.route("/<int:crop_id>/harvest", methods=["POST"])
@login_required
def harvest(crop_id):
    farmer = g.farmer
    crop = get_crop_by_id_and_farmer(crop_id, farmer["id"])
    if not crop:
        flash("Crop not found.", "danger")
        return redirect(url_for("crops.my_crops"))
    update_crop_status(crop_id, "harvested")
    flash(f"{crop['crop_name'].title()} marked as harvested.", "success")
    return redirect(url_for("crops.my_crops"))


# ── Delete Crop ────────────────────────────────────────────────────────────────

@crops_bp.route("/<int:crop_id>/delete", methods=["POST"])
@login_required
def delete(crop_id):
    farmer = g.farmer
    crop = get_crop_by_id_and_farmer(crop_id, farmer["id"])
    if not crop:
        flash("Crop not found.", "danger")
        return redirect(url_for("crops.my_crops"))
    delete_crop(crop_id, farmer["id"])
    flash(f"{crop['crop_name'].title()} removed from your farm.", "info")
    return redirect(url_for("crops.my_crops"))
