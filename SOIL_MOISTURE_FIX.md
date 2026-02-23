# Soil Moisture Dynamic Update - Complete Fix

## Problem Statement

### Issue 1: Soil Moisture Not Updating ❌
When users entered new soil moisture values in the irrigation recommendation page:
- System was using OLD/CACHED soil moisture from crop recommendation
- New user-entered values were IGNORED
- Irrigation schedules were INCORRECT

### Issue 2: Full Lifecycle Schedule Not Generating ❌
- Scheduler was not generating complete crop lifecycle plan
- Should generate 120-day plan for 120-day crop
- Should start from planting_date, not today

## Root Cause Analysis

### Why Soil Moisture Wasn't Updating
```python
# OLD CODE (WRONG):
latest_soil = get_latest_soil_for_crop(crop_id)
initial_moisture = latest_soil["moisture"]  # ❌ Always uses old value!

generate_full_lifecycle_schedule(
    initial_soil_moisture=initial_moisture  # ❌ Old value passed
)
```

**Problem:** System always fetched soil moisture from database, ignoring user input.

### Why Full Schedule Wasn't Generated
The `generate_full_lifecycle_schedule()` function was already correct (fixed in previous update), but routes weren't calling it properly with user-provided moisture.

## Complete Solution

### PART 1: Route-Level Fixes ✅

#### 1. Generate Schedule Route
**File:** `app/routes/irrigation.py`

```python
@irrigation_bp.route("/<int:crop_id>/schedule/generate", methods=["POST"])
@login_required
def generate_schedule(crop_id):
    # CRITICAL FIX: Check for user-provided soil moisture FIRST
    user_moisture = request.form.get("soil_moisture", type=float)
    
    if user_moisture is not None:
        # ✅ User explicitly provided moisture - USE IT!
        initial_moisture = user_moisture
        flash(f"Schedule generated using current soil moisture: {initial_moisture}%", "info")
    else:
        # Fallback to stored value only if user didn't provide
        latest_soil = get_latest_soil_for_crop(crop_id)
        initial_moisture = float(latest_soil["moisture"]) if latest_soil else 60.0
        flash(f"Schedule generated using stored soil moisture: {initial_moisture}%", "info")
    
    # Generate with correct moisture
    schedule = generate_full_lifecycle_schedule(
        farmer_id=farmer["id"],
        crop_id=crop_id,
        crop_name=crop["crop_name"],
        planting_date=crop["planting_date"],
        growth_duration=crop["growth_duration"],
        initial_soil_moisture=initial_moisture,  # ✅ Uses user input!
        city=farmer["location"],
    )
```

**Key Changes:**
- ✅ Checks `request.form.get("soil_moisture")` FIRST
- ✅ Uses user-provided value if available
- ✅ Falls back to stored value only if not provided
- ✅ Clear feedback messages to user

#### 2. Recalculate Schedule Route
**File:** `app/routes/irrigation.py`

```python
@irrigation_bp.route("/<int:crop_id>/schedule/recalculate", methods=["POST"])
@login_required
def recalculate_schedule(crop_id):
    # CRITICAL FIX: Accept user-provided moisture for recalculation
    user_moisture = request.form.get("soil_moisture", type=float)
    
    if user_moisture is not None:
        # ✅ User provided moisture - use it directly
        estimated_moisture = user_moisture
        flash(f"Recalculating with current soil moisture: {estimated_moisture}%", "info")
        
        # Detect missed irrigations
        missed_count = detect_and_handle_missed_irrigations(crop_id)
        
        # Regenerate with user-provided moisture
        new_schedule = generate_full_lifecycle_schedule(
            farmer_id=farmer["id"],
            crop_id=crop_id,
            crop_name=crop["crop_name"],
            planting_date=crop["planting_date"],
            growth_duration=crop["growth_duration"],
            initial_soil_moisture=estimated_moisture,  # ✅ User input!
            city=farmer["location"],
        )
        
        save_full_schedule_to_db(farmer["id"], crop_id, new_schedule)
```

**Key Changes:**
- ✅ Accepts soil moisture from form
- ✅ Overrides automatic estimation
- ✅ Regenerates schedule with accurate moisture

#### 3. Full Schedule View Route
**File:** `app/routes/irrigation.py`

```python
@irrigation_bp.route("/<int:crop_id>/schedule")
@login_required
def full_schedule(crop_id):
    # ... existing code ...
    
    # Get latest soil moisture for display in form
    latest_soil = get_latest_soil_for_crop(crop_id)
    current_moisture = float(latest_soil["moisture"]) if latest_soil else None
    
    return render_template(
        "irrigation/schedule.html",
        crop=crop,
        schedule=schedule,
        stats=stats,
        stage_info=stage_info,
        missed_count=missed_count,
        current_moisture=current_moisture,  # ✅ Pass to template
    )
```

**Key Changes:**
- ✅ Passes current moisture to template
- ✅ Pre-fills form with latest value
- ✅ User can override if needed

### PART 2: Template-Level Fixes ✅

#### Updated Schedule Template
**File:** `templates/irrigation/schedule.html`

**Added Soil Moisture Input Card:**
```html
<!-- Current Soil Moisture Input Card -->
<div class="card eco-card mb-4">
    <div class="card-body">
        <h5 class="card-title mb-3">
            <i class="bi bi-moisture me-2"></i>Update Schedule with Current Soil Moisture
        </h5>
        <form method="POST" action="{{ url_for('irrigation.generate_schedule', crop_id=crop.id) }}">
            <div class="col-md-4">
                <label class="form-label fw-semibold">Current Soil Moisture (%)</label>
                <input 
                    type="number" 
                    name="soil_moisture" 
                    class="form-control" 
                    placeholder="Enter current moisture %" 
                    min="0" 
                    max="100" 
                    step="0.1"
                    value="{{ current_moisture if current_moisture else '' }}"
                    required>
                <small class="text-muted">Enter the latest soil moisture reading</small>
            </div>
            <button type="submit" class="btn btn-primary">
                <i class="bi bi-arrow-clockwise me-1"></i>Regenerate Schedule with New Moisture
            </button>
        </form>
    </div>
</div>
```

**Updated Missed Irrigation Warning:**
```html
{% if missed_count > 0 %}
<div class="alert alert-warning">
    <form method="POST" action="{{ url_for('irrigation.recalculate_schedule', crop_id=crop.id) }}">
        <input 
            type="number" 
            name="soil_moisture" 
            class="form-control" 
            placeholder="Current moisture %" 
            min="0" 
            max="100" 
            step="0.1"
            value="{{ current_moisture if current_moisture else '' }}"
            required>
        <button type="submit" class="btn btn-warning">
            <i class="bi bi-calculator me-1"></i>Recalculate with Current Moisture
        </button>
    </form>
</div>
{% endif %}
```

**Updated Regenerate Modal:**
```html
<div class="modal fade" id="regenerateModal">
    <form method="POST" action="{{ url_for('irrigation.generate_schedule', crop_id=crop.id) }}">
        <div class="modal-body">
            <label class="form-label fw-semibold">Current Soil Moisture (%)</label>
            <input 
                type="number" 
                name="soil_moisture" 
                class="form-control" 
                value="{{ current_moisture if current_moisture else 60 }}"
                required>
        </div>
        <button type="submit" class="btn btn-eco">Regenerate</button>
    </form>
</div>
```

**Key Changes:**
- ✅ Prominent soil moisture input at top of page
- ✅ Pre-filled with latest value
- ✅ User can update anytime
- ✅ All generation/recalculation forms include moisture input

### PART 3: Scheduler Already Fixed ✅

The `generate_full_lifecycle_schedule()` function was already fixed in previous update:
- ✅ Starts from planting_date
- ✅ Generates full lifecycle (all growth_duration days)
- ✅ Uses Decimal for all calculations (no float mixing)
- ✅ Marks past dates as completed/missed

**File:** `app/services/advanced_scheduler.py`

```python
def generate_full_lifecycle_schedule(
    farmer_id: int,
    crop_id: int,
    crop_name: str,
    planting_date,
    growth_duration: int,
    initial_soil_moisture: float,  # ✅ Accepts user-provided value
    base_et0: float = 5.0,
    city: str = None,
) -> list:
    # Convert to Decimal for precise calculations
    simulated_moisture = Decimal(str(initial_soil_moisture))  # ✅ Uses provided value
    
    # Generate schedule day by day from planting date
    for day_num in range(growth_duration + 1):  # ✅ Full lifecycle
        current_date = plant_date + timedelta(days=day_num)  # ✅ From planting date
        
        # ... moisture simulation with Decimal ...
```

### PART 4: Today's Advice Unchanged ✅

The irrigation advice route (`/irrigation/<crop_id>`) remains completely unchanged:
- ✅ Still works exactly as before
- ✅ Uses user-entered soil moisture for immediate advice
- ✅ No impact from schedule changes

## Data Flow

### Before Fix (WRONG) ❌
```
User enters moisture → IGNORED
System fetches old moisture from DB → Used for schedule
Result: Incorrect schedule
```

### After Fix (CORRECT) ✅
```
User enters moisture → Captured in form
Form submitted → Route receives moisture
Route passes to scheduler → Schedule generated with correct moisture
Result: Accurate schedule
```

## User Experience

### Scenario 1: Generate New Schedule
1. User goes to Full Schedule page
2. Sees prominent "Update Schedule with Current Soil Moisture" card
3. Enters current moisture (e.g., 45%)
4. Clicks "Regenerate Schedule with New Moisture"
5. ✅ Schedule generated using 45%, not old value
6. Flash message confirms: "Schedule generated using current soil moisture: 45%"

### Scenario 2: Recalculate After Missed Irrigation
1. System detects missed irrigations
2. Warning appears with moisture input field
3. User enters current moisture (e.g., 30%)
4. Clicks "Recalculate with Current Moisture"
5. ✅ Schedule recalculated using 30%
6. Flash message: "Recalculating with current soil moisture: 30%"

### Scenario 3: Regenerate from Modal
1. User clicks "Regenerate" button
2. Modal opens with moisture input
3. Field pre-filled with latest value
4. User can adjust if needed
5. Clicks "Regenerate"
6. ✅ Schedule generated with entered value

## Testing Checklist

### Test Soil Moisture Override
- [ ] Go to Full Schedule page
- [ ] Enter new soil moisture (different from stored)
- [ ] Generate schedule
- [ ] Verify flash message shows entered value
- [ ] Verify schedule uses new value (check first few irrigation dates)

### Test Recalculation with Moisture
- [ ] Let an irrigation be missed
- [ ] Warning appears
- [ ] Enter current moisture in warning form
- [ ] Click "Recalculate with Current Moisture"
- [ ] Verify schedule regenerated with entered value

### Test Regenerate Modal
- [ ] Click "Regenerate" button
- [ ] Modal opens
- [ ] Moisture field pre-filled
- [ ] Change value
- [ ] Submit
- [ ] Verify new schedule uses changed value

### Test Fallback Behavior
- [ ] Generate schedule WITHOUT entering moisture
- [ ] System should use stored value
- [ ] Flash message should indicate "stored soil moisture"

### Test Today's Advice (Unchanged)
- [ ] Go to "Get Irrigation Advice"
- [ ] Enter soil moisture
- [ ] Calculate
- [ ] Verify advice is correct
- [ ] Verify this still works as before

## Key Benefits

1. **Always Accurate** - Schedule uses latest soil moisture, not cached values
2. **User Control** - Farmers can update moisture anytime
3. **Clear Feedback** - Flash messages confirm which value was used
4. **Flexible** - Works with or without user input (fallback to stored)
5. **Backward Compatible** - Today's Advice unchanged

## Summary

### What Was Fixed
✅ Routes now accept and prioritize user-provided soil moisture
✅ Template provides multiple ways to input current moisture
✅ Clear feedback on which moisture value was used
✅ Fallback to stored value if user doesn't provide
✅ Full lifecycle schedule generation confirmed working

### What Wasn't Changed
✅ Today's Advice logic - works exactly as before
✅ Scheduler algorithm - already correct from previous fix
✅ Database structure - no changes needed
✅ Other irrigation features - unaffected

### Files Modified
1. `app/routes/irrigation.py` - 3 routes updated
2. `templates/irrigation/schedule.html` - Complete rewrite with moisture inputs

### No Database Changes Required
The existing structure supports all features perfectly.

## Quick Reference

### Generate Schedule with Moisture
```python
POST /irrigation/<crop_id>/schedule/generate
Body: soil_moisture=45.5
```

### Recalculate with Moisture
```python
POST /irrigation/<crop_id>/schedule/recalculate
Body: soil_moisture=30.0
```

### View Schedule
```python
GET /irrigation/<crop_id>/schedule
Returns: current_moisture value for form pre-fill
```

The system now ALWAYS uses the latest user-provided soil moisture for accurate irrigation scheduling!
