"""
Irrigation Engine — stage detection, ET₀ calculation, and irrigation advice.
"""
from datetime import datetime, date


# ── Stage generation ───────────────────────────────────────────────────────────

def generate_crop_stages(total_days: int) -> dict:
    """
    Split total growing period into 4 FAO-56 stages with Kc coefficients.
    Proportions: initial 20 %, development 30 %, mid-season 30 %, late 20 %.
    """
    return {
        "Initial": {
            "duration": int(total_days * 0.20),
            "kc": 0.70,
            "description": "Germination & early vegetative growth",
        },
        "Development": {
            "duration": int(total_days * 0.30),
            "kc": 0.95,
            "description": "Rapid canopy development",
        },
        "Mid-Season": {
            "duration": int(total_days * 0.30),
            "kc": 1.15,
            "description": "Full canopy – peak water demand",
        },
        "Late": {
            "duration": int(total_days * 0.20),
            "kc": 0.80,
            "description": "Ripening & senescence",
        },
    }


# ── Stage detection ────────────────────────────────────────────────────────────

def get_current_stage(planting_date_str, total_days: int) -> dict:
    """
    Given a planting date (YYYY-MM-DD string or date object) and crop duration, return:
    stage_name, kc, days_after_sowing, progress_pct, description.
    """
    # Handle both string and date object inputs
    if isinstance(planting_date_str, str):
        try:
            plant_dt = datetime.strptime(planting_date_str, "%Y-%m-%d").date()
        except ValueError:
            plant_dt = date.today()
    elif isinstance(planting_date_str, date):
        plant_dt = planting_date_str
    else:
        plant_dt = date.today()

    days_after_sowing = (date.today() - plant_dt).days
    days_after_sowing = max(days_after_sowing, 0)

    stages = generate_crop_stages(total_days)

    # Harvest-ready check
    if days_after_sowing >= total_days:
        return {
            "stage_name": "Harvest-Ready",
            "kc": 0.60,
            "days_after_sowing": days_after_sowing,
            "progress_pct": 100,
            "description": "Crop has completed its growth cycle",
        }

    cumulative = 0
    for stage_name, data in stages.items():
        cumulative += data["duration"]
        if days_after_sowing < cumulative:
            progress_pct = int((days_after_sowing / total_days) * 100)
            return {
                "stage_name": stage_name,
                "kc": data["kc"],
                "days_after_sowing": days_after_sowing,
                "progress_pct": min(progress_pct, 99),
                "description": data["description"],
            }

    # Fallback
    return {
        "stage_name": "Late",
        "kc": 0.80,
        "days_after_sowing": days_after_sowing,
        "progress_pct": 95,
        "description": "Ripening & senescence",
    }



# ── ET₀ & irrigation calculation ──────────────────────────────────────────────

def calculate_irrigation(
    temperature: float,
    rainfall: float,
    kc: float,
    soil_moisture: float,
) -> dict:
    """
    Calculate irrigation requirement using simplified Penman-Monteith ET₀.

    Returns dict with: et0, etc, net_water, decision, badge_class.
    """
    # Simplified ET₀ (Hargreaves approximation)
    et0 = max(0.0, 0.5 * temperature)
    crop_etc = round(et0 * kc, 3)
    net_water = max(round(crop_etc - rainfall, 3), 0.0)

    # Decision logic
    if soil_moisture > 70:
        decision = "No irrigation needed — soil moisture is adequate"
        badge = "success"
        net_water = 0.0
    elif soil_moisture < 30:
        decision = "Urgent irrigation required — soil critically dry"
        badge = "danger"
    elif net_water == 0:
        decision = "No irrigation needed — rainfall is sufficient"
        badge = "success"
    elif net_water < 3:
        decision = "Light irrigation recommended"
        badge = "info"
    elif net_water < 6:
        decision = "Moderate irrigation required"
        badge = "warning"
    else:
        decision = "Full irrigation required"
        badge = "danger"

    return {
        "et0": round(et0, 3),
        "etc": crop_etc,
        "net_water": net_water,
        "decision": decision,
        "badge": badge,
    }


# ── Weekly plan ────────────────────────────────────────────────────────────────

def get_weekly_plan(forecast: list, base_water: float, soil_moisture: float) -> list:
    """
    Build a 5-day irrigation plan from forecast data.
    Returns list of dicts: date, temp, humidity, rain, decision, water, saved.
    """
    plan = []
    for day in forecast:
        rain = day["rain"]
        temp = day["temp"]

        if rain > 5:
            decision = "Rain expected — skip irrigation"
            water = 0.0
            saved = base_water
            badge = "info"
        elif soil_moisture > 70:
            decision = "Soil wet — no irrigation"
            water = 0.0
            saved = base_water
            badge = "success"
        elif temp > 34:
            decision = "Hot day — full irrigation"
            water = round(base_water * 1.2, 2)
            saved = 0.0
            badge = "danger"
        else:
            decision = "Normal irrigation"
            water = base_water
            saved = 0.0
            badge = "warning"

        plan.append({
            "date": day["date"],
            "temp": temp,
            "humidity": day["humidity"],
            "rain": rain,
            "decision": decision,
            "water": water,
            "saved": saved,
            "badge": badge,
        })
    return plan
