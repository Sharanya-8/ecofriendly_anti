"""
Irrigation Scheduler — 30-day schedule generation and missed irrigation handling.
"""
from datetime import datetime, date, timedelta
from app.database import query_db, execute_db, transaction


def calculate_irrigation_interval(
    kc: float,
    et0: float,
    soil_moisture: float,
    rainfall: float = 0,
    field_capacity: float = 100,
) -> int:
    """
    Calculate days until next irrigation based on water balance.
    
    Returns number of days before next irrigation is needed.
    """
    # Daily water consumption (mm/day)
    daily_etc = et0 * kc
    
    # Available water in soil (as percentage of field capacity)
    available_water = soil_moisture
    
    # Adjust for rainfall
    effective_rain = rainfall * 0.8  # 80% efficiency
    
    # Calculate depletion rate
    if daily_etc <= 0:
        return 7  # Default interval if no consumption
    
    # Days until soil reaches 30% moisture (critical threshold)
    critical_threshold = 30
    water_to_deplete = available_water - critical_threshold + effective_rain
    
    days_until_irrigation = max(1, int(water_to_deplete / daily_etc))
    
    # Cap between 2-10 days for practical scheduling
    return min(max(days_until_irrigation, 2), 10)


def generate_30day_schedule(
    farmer_id: int,
    crop_id: int,
    crop_name: str,
    planting_date: str,
    growth_duration: int,
    current_soil_moisture: float,
    base_et0: float,
    city: str,
    forecast_data: list = None,
) -> list:
    """
    Generate a 30-day irrigation schedule for a crop.
    
    Returns list of schedule entries: {date, water_amount, reason, interval_days}
    """
    from app.services.irrigation_engine import get_current_stage, generate_crop_stages
    from app.services.ml_engine import get_water_need
    
    schedule = []
    current_date = date.today()
    end_date = current_date + timedelta(days=30)
    
    # Get crop stages
    stages = generate_crop_stages(growth_duration)
    base_water = get_water_need(crop_name)
    
    # Simulate soil moisture over 30 days
    simulated_moisture = current_soil_moisture
    next_irrigation_date = current_date
    
    day_count = 0
    while next_irrigation_date <= end_date and day_count < 30:
        # Get current stage for this date
        days_from_planting = (next_irrigation_date - datetime.strptime(planting_date, "%Y-%m-%d").date()).days
        stage_info = get_current_stage(planting_date, growth_duration)
        
        # Check if crop is harvest-ready
        if days_from_planting >= growth_duration:
            break
        
        kc = stage_info["kc"]
        
        # Get forecast rainfall if available
        rainfall = 0
        if forecast_data:
            for forecast in forecast_data:
                if forecast.get("date") == str(next_irrigation_date):
                    rainfall = forecast.get("rain", 0)
                    break
        
        # Calculate water requirement
        daily_etc = base_et0 * kc
        water_amount = round(base_water * kc, 2)
        
        # Determine if irrigation is needed
        reason = f"{stage_info['stage_name']} stage"
        
        if rainfall > 5:
            reason = f"Rain expected ({rainfall}mm) - Skip irrigation"
            water_amount = 0
            interval = 5  # Check again after rain
        elif simulated_moisture > 70:
            reason = "Soil moisture adequate - Skip irrigation"
            water_amount = 0
            interval = 4
        else:
            reason = f"{stage_info['stage_name']} stage - Irrigation required"
            interval = calculate_irrigation_interval(kc, base_et0, simulated_moisture, rainfall)
            simulated_moisture = 80  # Reset after irrigation
        
        schedule.append({
            "scheduled_date": next_irrigation_date,
            "water_amount": water_amount,
            "reason": reason,
            "interval_days": interval,
            "stage": stage_info["stage_name"],
            "kc": kc,
        })
        
        # Move to next irrigation date
        next_irrigation_date += timedelta(days=interval)
        
        # Simulate moisture depletion
        simulated_moisture -= (daily_etc * interval * 0.5)  # Simplified depletion
        simulated_moisture = max(simulated_moisture, 20)
        
        day_count += interval
    
    return schedule


def save_schedule_to_db(farmer_id: int, crop_id: int, schedule: list):
    """
    Save generated schedule to IrrigationSchedule table.
    Clears existing pending schedules for the crop first.
    """
    with transaction():
        # Clear old pending schedules
        execute_db(
            "DELETE FROM IrrigationSchedule WHERE crop_id = %s AND status = 'pending'",
            (crop_id,)
        )
        
        # Insert new schedule
        for entry in schedule:
            execute_db(
                """
                INSERT INTO IrrigationSchedule 
                    (farmer_id, crop_id, scheduled_date, water_amount, status, reason)
                VALUES (%s, %s, %s, %s, 'pending', %s)
                """,
                (
                    farmer_id,
                    crop_id,
                    entry["scheduled_date"],
                    entry["water_amount"],
                    entry["reason"],
                )
            )


def get_schedule_for_crop(crop_id: int, days: int = 30):
    """Retrieve upcoming irrigation schedule for a crop."""
    today = date.today()
    end_date = today + timedelta(days=days)
    
    return query_db(
        """
        SELECT * FROM IrrigationSchedule
        WHERE crop_id = %s 
          AND scheduled_date BETWEEN %s AND %s
        ORDER BY scheduled_date ASC
        """,
        (crop_id, today, end_date)
    )


def get_todays_schedule(farmer_id: int):
    """Get all irrigation tasks scheduled for today."""
    today = date.today()
    
    return query_db(
        """
        SELECT s.*, c.crop_name, c.field_name
        FROM IrrigationSchedule s
        JOIN Crops c ON c.id = s.crop_id
        WHERE s.farmer_id = %s 
          AND s.scheduled_date = %s
          AND s.status = 'pending'
        ORDER BY c.field_name
        """,
        (farmer_id, today)
    )


def mark_irrigation_completed(schedule_id: int, actual_water: float = None):
    """Mark a scheduled irrigation as completed."""
    if actual_water is None:
        execute_db(
            """
            UPDATE IrrigationSchedule 
            SET status = 'completed', completed_at = NOW()
            WHERE id = %s
            """,
            (schedule_id,)
        )
    else:
        execute_db(
            """
            UPDATE IrrigationSchedule 
            SET status = 'completed', completed_at = NOW(), water_amount = %s
            WHERE id = %s
            """,
            (actual_water, schedule_id)
        )


def detect_missed_irrigations(crop_id: int):
    """
    Detect and mark missed irrigation schedules.
    Returns list of missed irrigation dates.
    """
    today = date.today()
    
    # Find pending schedules that are overdue
    missed = query_db(
        """
        SELECT * FROM IrrigationSchedule
        WHERE crop_id = %s 
          AND scheduled_date < %s
          AND status = 'pending'
        ORDER BY scheduled_date
        """,
        (crop_id, today)
    )
    
    # Mark them as missed
    if missed:
        execute_db(
            """
            UPDATE IrrigationSchedule
            SET status = 'missed'
            WHERE crop_id = %s 
              AND scheduled_date < %s
              AND status = 'pending'
            """,
            (crop_id, today)
        )
    
    return missed


def recalculate_schedule_after_missed(
    farmer_id: int,
    crop_id: int,
    crop_name: str,
    planting_date: str,
    growth_duration: int,
    days_missed: int,
    base_et0: float,
    city: str,
):
    """
    Recalculate irrigation schedule after missed irrigation(s).
    
    Adjusts soil moisture deficit and regenerates schedule.
    """
    from app.services.ml_engine import get_water_need
    
    # Estimate current soil moisture after missed days
    # Assume 5% depletion per missed day (simplified)
    estimated_moisture = max(20, 70 - (days_missed * 5))
    
    # Check if immediate irrigation is critical
    immediate_irrigation = estimated_moisture < 30
    
    # Regenerate schedule with adjusted moisture
    new_schedule = generate_30day_schedule(
        farmer_id=farmer_id,
        crop_id=crop_id,
        crop_name=crop_name,
        planting_date=planting_date,
        growth_duration=growth_duration,
        current_soil_moisture=estimated_moisture,
        base_et0=base_et0,
        city=city,
    )
    
    # Save new schedule
    save_schedule_to_db(farmer_id, crop_id, new_schedule)
    
    return {
        "immediate_irrigation_needed": immediate_irrigation,
        "estimated_moisture": estimated_moisture,
        "days_missed": days_missed,
        "new_schedule": new_schedule[:7],  # Return first week
    }


def get_schedule_summary(farmer_id: int):
    """Get summary of all upcoming irrigations for farmer's dashboard."""
    today = date.today()
    week_end = today + timedelta(days=7)
    
    return query_db(
        """
        SELECT 
            s.scheduled_date,
            s.water_amount,
            s.status,
            c.crop_name,
            c.field_name,
            s.reason
        FROM IrrigationSchedule s
        JOIN Crops c ON c.id = s.crop_id
        WHERE s.farmer_id = %s 
          AND s.scheduled_date BETWEEN %s AND %s
          AND s.status IN ('pending', 'missed')
        ORDER BY s.scheduled_date, c.field_name
        """,
        (farmer_id, today, week_end)
    )
