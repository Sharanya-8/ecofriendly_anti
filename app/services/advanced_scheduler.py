"""
Advanced Irrigation Scheduler — Full crop lifecycle scheduling with dynamic adjustments.

This module generates irrigation schedules from planting date to harvest,
with automatic recalculation based on weather and irrigation history.
"""
from datetime import datetime, date, timedelta
from decimal import Decimal
from app.database import query_db, execute_db, transaction
from app.services.irrigation_engine import generate_crop_stages


def check_if_irrigated(crop_id: int, check_date: date) -> str:
    """
    Check if irrigation was completed on a specific date.
    Returns 'completed' if found in history, 'missed' otherwise.
    """
    # Check IrrigationSchedule table
    existing = query_db(
        """
        SELECT status FROM IrrigationSchedule
        WHERE crop_id = %s AND scheduled_date = %s
        """,
        (crop_id, check_date),
        one=True
    )
    
    if existing:
        return existing["status"]
    
    # Check IrrigationHistory table
    history = query_db(
        """
        SELECT id FROM IrrigationHistory
        WHERE crop_id = %s 
          AND DATE(recorded_at) = %s
        """,
        (crop_id, check_date),
        one=True
    )
    
    return 'completed' if history else 'missed'


def generate_full_lifecycle_schedule(
    farmer_id: int,
    crop_id: int,
    crop_name: str,
    planting_date,  # Can be string or date object
    growth_duration: int,
    initial_soil_moisture: float,
    base_et0: float = 5.0,
    city: str = None,
) -> list:
    """
    Generate complete irrigation schedule from planting date to harvest.
    
    FIXED: Starts from planting_date, not today
    FIXED: Generates full lifecycle (all growth_duration days)
    FIXED: Uses Decimal for all moisture calculations (no float mixing)
    FIXED: Marks past dates as completed/missed based on history
    
    Args:
        farmer_id: Farmer ID
        crop_id: Crop ID
        crop_name: Name of the crop
        planting_date: Planting date (string YYYY-MM-DD or date object)
        growth_duration: Total days from planting to harvest
        initial_soil_moisture: Starting soil moisture percentage
        base_et0: Base evapotranspiration rate (mm/day)
        city: City for weather data (optional)
    
    Returns:
        List of schedule entries with date, water_amount, stage, reason, status
    """
    from app.services.ml_engine import get_water_need
    
    # Normalize planting date
    if isinstance(planting_date, str):
        plant_date = datetime.strptime(planting_date, "%Y-%m-%d").date()
    elif isinstance(planting_date, date):
        plant_date = planting_date
    else:
        plant_date = date.today()
    
    # Convert to Decimal for precise calculations (FIX: No float mixing)
    simulated_moisture = Decimal(str(initial_soil_moisture))
    base_et0_decimal = Decimal(str(base_et0))
    
    # Get crop stages
    stages = generate_crop_stages(growth_duration)
    base_water = get_water_need(crop_name)
    base_water_decimal = Decimal(str(base_water))
    
    schedule = []
    harvest_date = plant_date + timedelta(days=growth_duration)
    today = date.today()
    
    # Track cumulative days for stage detection
    cumulative_days = 0
    stage_boundaries = []
    for stage_name, stage_data in stages.items():
        cumulative_days += stage_data["duration"]
        stage_boundaries.append({
            "name": stage_name,
            "end_day": cumulative_days,
            "kc": Decimal(str(stage_data["kc"])),
            "description": stage_data["description"]
        })
    
    # Generate schedule day by day from planting date (FIX: Start from planting_date)
    last_irrigation_day = 0
    
    for day_num in range(growth_duration + 1):
        current_date = plant_date + timedelta(days=day_num)
        
        # Stop if we've reached harvest
        if current_date > harvest_date:
            break
        
        # Determine current stage
        current_stage = None
        for boundary in stage_boundaries:
            if day_num < boundary["end_day"]:
                current_stage = boundary
                break
        
        if not current_stage:
            current_stage = stage_boundaries[-1]  # Late stage
        
        kc = current_stage["kc"]
        stage_name = current_stage["name"]
        
        # Calculate daily water consumption (all Decimal - FIX: No float mixing)
        daily_etc = base_et0_decimal * kc
        
        # Simulate moisture depletion (Decimal-safe - FIX: No float mixing)
        depletion_factor = Decimal("0.15")
        simulated_moisture -= (daily_etc * depletion_factor)
        simulated_moisture = max(simulated_moisture, Decimal("15"))
        
        # Determine if irrigation is needed
        days_since_last_irrigation = day_num - last_irrigation_day
        
        # Irrigation decision logic
        needs_irrigation = False
        reason = f"{stage_name} stage"
        water_amount = Decimal("0")
        
        # Critical moisture level
        if simulated_moisture < Decimal("35"):
            needs_irrigation = True
            reason = f"{stage_name} - Critical moisture level"
            water_amount = base_water_decimal * kc * Decimal("1.2")  # Extra water
        # Regular irrigation needed
        elif simulated_moisture < Decimal("50") and days_since_last_irrigation >= 3:
            needs_irrigation = True
            reason = f"{stage_name} - Regular irrigation"
            water_amount = base_water_decimal * kc
        # Maintenance irrigation
        elif days_since_last_irrigation >= 7:
            needs_irrigation = True
            reason = f"{stage_name} - Maintenance irrigation"
            water_amount = base_water_decimal * kc * Decimal("0.8")
        
        # Add to schedule if irrigation is needed
        if needs_irrigation:
            # Determine status based on date (FIX: Mark past dates properly)
            if current_date < today:
                # Past date - check if it was actually irrigated
                status = check_if_irrigated(crop_id, current_date)
            elif current_date == today:
                status = 'pending'
            else:
                status = 'pending'
            
            schedule.append({
                "scheduled_date": current_date,
                "water_amount": float(round(water_amount, 2)),  # Convert back to float for DB
                "reason": reason,
                "stage": stage_name,
                "kc": float(kc),
                "days_after_sowing": day_num,
                "estimated_moisture": float(round(simulated_moisture, 1)),
                "status": status,
            })
            
            # Reset moisture after irrigation (Decimal-safe)
            moisture_increase = Decimal("40")
            simulated_moisture = min(simulated_moisture + moisture_increase, Decimal("85"))
            last_irrigation_day = day_num
    
    return schedule


def save_full_schedule_to_db(farmer_id: int, crop_id: int, schedule: list):
    """
    Save complete lifecycle schedule to database.
    Preserves completed/missed status for past dates.
    """
    with transaction():
        # Clear future pending schedules only
        today = date.today()
        execute_db(
            """
            DELETE FROM IrrigationSchedule 
            WHERE crop_id = %s 
              AND scheduled_date >= %s 
              AND status = 'pending'
            """,
            (crop_id, today)
        )
        
        # Insert new schedule
        for entry in schedule:
            # Check if entry already exists
            existing = query_db(
                """
                SELECT id, status FROM IrrigationSchedule
                WHERE crop_id = %s AND scheduled_date = %s
                """,
                (crop_id, entry["scheduled_date"]),
                one=True
            )
            
            if existing:
                # Update only if status is pending
                if existing["status"] == "pending":
                    execute_db(
                        """
                        UPDATE IrrigationSchedule
                        SET water_amount = %s, reason = %s
                        WHERE id = %s
                        """,
                        (entry["water_amount"], entry["reason"], existing["id"])
                    )
            else:
                # Insert new entry with proper status
                execute_db(
                    """
                    INSERT INTO IrrigationSchedule 
                        (farmer_id, crop_id, scheduled_date, water_amount, status, reason)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        farmer_id,
                        crop_id,
                        entry["scheduled_date"],
                        entry["water_amount"],
                        entry.get("status", "pending"),
                        entry["reason"],
                    )
                )


def mark_irrigation_done(schedule_id: int, actual_water: float = None):
    """
    Mark irrigation as completed and optionally record actual water used.
    Also creates entry in IrrigationHistory.
    """
    from app.models.irrigation import add_irrigation_record
    
    # Get schedule details
    schedule = query_db(
        """
        SELECT s.*, c.crop_name, c.planting_date, c.growth_duration, f.location
        FROM IrrigationSchedule s
        JOIN Crops c ON c.id = s.crop_id
        JOIN Farmers f ON f.id = s.farmer_id
        WHERE s.id = %s
        """,
        (schedule_id,),
        one=True
    )
    
    if not schedule:
        return False
    
    water_used = actual_water if actual_water else schedule["water_amount"]
    
    with transaction():
        # Update schedule status
        execute_db(
            """
            UPDATE IrrigationSchedule
            SET status = 'completed', 
                completed_at = NOW(),
                water_amount = %s
            WHERE id = %s
            """,
            (water_used, schedule_id)
        )
        
        # Add to irrigation history
        from app.services.irrigation_engine import get_current_stage
        stage_info = get_current_stage(
            schedule["planting_date"],
            schedule["growth_duration"]
        )
        
        add_irrigation_record(
            farmer_id=schedule["farmer_id"],
            crop_id=schedule["crop_id"],
            city=schedule["location"],
            stage=stage_info["stage_name"],
            days_after_sowing=stage_info["days_after_sowing"],
            et0=5.0,  # Default ET0
            kc=stage_info["kc"],
            water_required=water_used,
            decision=f"Scheduled irrigation completed - {schedule['reason']}",
        )
    
    return True


def detect_and_handle_missed_irrigations(crop_id: int):
    """
    Detect missed irrigations and mark them.
    Returns count of missed irrigations.
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
    
    if missed:
        # Mark as missed
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
    
    return len(missed) if missed else 0


def recalculate_after_missed_irrigation(
    farmer_id: int,
    crop_id: int,
    crop_name: str,
    planting_date,
    growth_duration: int,
    city: str,
):
    """
    Recalculate schedule after detecting missed irrigations.
    Adjusts future schedule based on estimated soil moisture deficit.
    """
    # Count missed irrigations
    missed_count = detect_and_handle_missed_irrigations(crop_id)
    
    if missed_count == 0:
        return {"recalculated": False, "missed_count": 0}
    
    # Estimate current soil moisture (pessimistic)
    # Each missed day reduces moisture by ~5%
    estimated_moisture = max(20, 70 - (missed_count * 5))
    
    # Get latest soil reading if available
    from app.models.soil import get_latest_soil_for_crop
    latest_soil = get_latest_soil_for_crop(crop_id)
    if latest_soil:
        estimated_moisture = float(latest_soil["moisture"])
    
    # Regenerate schedule from planting date (includes past dates)
    new_schedule = generate_full_lifecycle_schedule(
        farmer_id=farmer_id,
        crop_id=crop_id,
        crop_name=crop_name,
        planting_date=planting_date,
        growth_duration=growth_duration,
        initial_soil_moisture=estimated_moisture,
        city=city,
    )
    
    # Save new schedule
    save_full_schedule_to_db(farmer_id, crop_id, new_schedule)
    
    # Get next upcoming irrigation
    next_irrigation = None
    today = date.today()
    for entry in new_schedule:
        if entry["scheduled_date"] >= today and entry.get("status") == "pending":
            next_irrigation = entry
            break
    
    return {
        "recalculated": True,
        "missed_count": missed_count,
        "estimated_moisture": estimated_moisture,
        "urgent_irrigation": estimated_moisture < 30,
        "next_irrigation": next_irrigation,
    }


def get_full_schedule_for_crop(crop_id: int):
    """Get complete irrigation schedule for a crop (past and future)."""
    return query_db(
        """
        SELECT * FROM IrrigationSchedule
        WHERE crop_id = %s
        ORDER BY scheduled_date ASC
        """,
        (crop_id,)
    )


def get_schedule_statistics(crop_id: int) -> dict:
    """Get statistics about irrigation schedule adherence."""
    stats = query_db(
        """
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
            SUM(CASE WHEN status = 'missed' THEN 1 ELSE 0 END) as missed,
            SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
            SUM(CASE WHEN status = 'skipped' THEN 1 ELSE 0 END) as skipped
        FROM IrrigationSchedule
        WHERE crop_id = %s
        """,
        (crop_id,),
        one=True
    )
    
    if not stats or stats["total"] == 0:
        return {
            "total": 0,
            "completed": 0,
            "missed": 0,
            "pending": 0,
            "skipped": 0,
            "adherence_rate": 0,
        }
    
    adherence_rate = (stats["completed"] / stats["total"]) * 100 if stats["total"] > 0 else 0
    
    return {
        "total": stats["total"],
        "completed": stats["completed"],
        "missed": stats["missed"],
        "pending": stats["pending"],
        "skipped": stats["skipped"],
        "adherence_rate": round(adherence_rate, 1),
    }
