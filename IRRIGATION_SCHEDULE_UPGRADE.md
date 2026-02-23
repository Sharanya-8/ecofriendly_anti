# Irrigation Scheduling System - Complete Upgrade

## Overview

The irrigation scheduling system has been upgraded to provide **full crop lifecycle scheduling** from planting date to harvest, with dynamic recalculation based on weather and irrigation history.

## Key Features

### 1. Full Lifecycle Scheduling
- Generates irrigation schedule from **planting date** to **harvest date**
- Covers entire growth duration (e.g., 120 days for a crop)
- Schedules based on crop growth stages (Initial, Development, Mid-Season, Late)

### 2. Dynamic Recalculation
- Automatically detects missed irrigations
- Recalculates future schedule based on:
  - Missed irrigation events
  - Current soil moisture deficit
  - Weather conditions
  - Crop stage requirements

### 3. "I Irrigated Today" Feature
- Button to mark irrigation as completed
- Records actual water used
- Automatically creates entry in IrrigationHistory
- Updates schedule status

### 4. Smart Scheduling Logic
- Uses crop coefficient (Kc) for each growth stage
- Considers soil moisture levels
- Adjusts for weather forecasts
- Prevents over-irrigation

### 5. Schedule Statistics
- Total irrigation events
- Completed vs Missed vs Pending
- Adherence rate percentage
- Visual progress tracking

## Architecture

### New Files Created

1. **app/services/advanced_scheduler.py**
   - `generate_full_lifecycle_schedule()` - Main scheduling algorithm
   - `save_full_schedule_to_db()` - Persist schedule to database
   - `mark_irrigation_done()` - Mark irrigation complete
   - `detect_and_handle_missed_irrigations()` - Find missed events
   - `recalculate_after_missed_irrigation()` - Regenerate schedule
   - `get_schedule_statistics()` - Calculate adherence metrics

2. **templates/irrigation/schedule.html**
   - Full schedule timeline view
   - Statistics dashboard
   - "Mark as Done" buttons
   - Recalculate functionality

### Modified Files

1. **app/routes/irrigation.py**
   - Added `/irrigation/<crop_id>/schedule` - View full schedule
   - Added `/irrigation/<crop_id>/schedule/generate` - Generate schedule
   - Added `/irrigation/schedule/<id>/complete` - Mark irrigation done
   - Added `/irrigation/<crop_id>/schedule/recalculate` - Recalculate schedule

2. **templates/irrigation/dashboard.html**
   - Added "Full Schedule" button for each crop

## Database Structure

### Existing Table: IrrigationSchedule

The existing table structure is perfect and requires **NO CHANGES**:

```sql
CREATE TABLE IrrigationSchedule (
    id INT AUTO_INCREMENT PRIMARY KEY,
    farmer_id INT NOT NULL,
    crop_id INT NOT NULL,
    scheduled_date DATE NOT NULL,
    water_amount DECIMAL(10,3) NOT NULL,
    status ENUM('pending', 'completed', 'missed', 'skipped') DEFAULT 'pending',
    reason TEXT,
    completed_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (farmer_id) REFERENCES Farmers(id) ON DELETE CASCADE,
    FOREIGN KEY (crop_id) REFERENCES Crops(id) ON DELETE CASCADE,
    INDEX idx_farmer_date (farmer_id, scheduled_date),
    INDEX idx_crop_status (crop_id, status),
    INDEX idx_scheduled_date (scheduled_date),
    UNIQUE KEY unique_crop_date (crop_id, scheduled_date)
) ENGINE=InnoDB;
```

### Status Values Explained

- **pending**: Irrigation scheduled but not yet done
- **completed**: Irrigation was performed
- **missed**: Irrigation was scheduled but not done (past date)
- **skipped**: Irrigation was intentionally skipped (e.g., due to rain)

## How It Works

### 1. Schedule Generation

When a farmer adds a crop or clicks "Generate Schedule":

```python
schedule = generate_full_lifecycle_schedule(
    farmer_id=farmer_id,
    crop_id=crop_id,
    crop_name="wheat",
    planting_date="2024-10-01",  # Actual planting date
    growth_duration=120,          # Days to harvest
    initial_soil_moisture=60.0,   # Current moisture %
    city="Hyderabad"
)
```

**Algorithm:**
1. Calculate crop stages (Initial 20%, Development 30%, Mid-Season 30%, Late 20%)
2. For each day from planting to harvest:
   - Determine current growth stage
   - Calculate water requirement using Kc coefficient
   - Simulate soil moisture depletion
   - Schedule irrigation when moisture drops below threshold
3. Save schedule to database

### 2. Marking Irrigation Complete

When farmer clicks "I Irrigated Today":

1. Updates schedule status to 'completed'
2. Records actual water used
3. Creates entry in IrrigationHistory table
4. Updates completed_at timestamp

### 3. Missed Irrigation Detection

System automatically detects missed irrigations:

```python
missed_count = detect_and_handle_missed_irrigations(crop_id)
```

- Finds all 'pending' schedules with date < today
- Marks them as 'missed'
- Returns count of missed events

### 4. Schedule Recalculation

When irrigations are missed:

```python
result = recalculate_after_missed_irrigation(
    farmer_id=farmer_id,
    crop_id=crop_id,
    crop_name=crop_name,
    planting_date=planting_date,
    growth_duration=growth_duration,
    city=city
)
```

**Recalculation Logic:**
1. Count missed irrigations
2. Estimate current soil moisture (pessimistic: -5% per missed day)
3. Check if urgent irrigation needed (moisture < 30%)
4. Regenerate schedule from today with adjusted moisture
5. Clear old pending schedules
6. Save new schedule

## User Interface

### Schedule View Features

1. **Statistics Cards**
   - Total Events
   - Completed
   - Upcoming (Pending)
   - Missed

2. **Adherence Rate**
   - Visual progress bar
   - Percentage calculation
   - Color-coded (Green ≥80%, Yellow ≥60%, Red <60%)

3. **Timeline Table**
   - Date and Day number
   - Growth stage
   - Water amount
   - Status badge
   - Reason/Description
   - Action buttons

4. **Action Buttons**
   - "Done" - Mark today's irrigation complete
   - "Recalculate" - Regenerate schedule after missed events
   - "Regenerate" - Create fresh schedule

## Separation of Concerns

### Today's Advice (UNCHANGED)
- Route: `/irrigation/<crop_id>`
- Purpose: Get immediate irrigation advice for today
- Uses: Real-time weather, current soil moisture
- Function: `calculate_irrigation()` in `irrigation_engine.py`
- **Status: NOT MODIFIED - Works as before**

### Full Schedule (NEW)
- Route: `/irrigation/<crop_id>/schedule`
- Purpose: View complete crop lifecycle schedule
- Uses: Planting date, growth duration, historical data
- Function: `generate_full_lifecycle_schedule()` in `advanced_scheduler.py`
- **Status: NEW FEATURE**

### 5-Day Planner (UNCHANGED)
- Route: `/irrigation/<crop_id>/weekly`
- Purpose: Short-term 5-day forecast-based plan
- Uses: Weather forecast
- Function: `get_weekly_plan()` in `irrigation_engine.py`
- **Status: NOT MODIFIED - Works as before**

## Database Commands

### No Changes Required!

The existing database structure is perfect. However, if you want to verify or reset:

### View Current Schedules
```sql
-- View all schedules for a crop
SELECT * FROM IrrigationSchedule 
WHERE crop_id = 1 
ORDER BY scheduled_date;

-- View today's pending irrigations
SELECT s.*, c.crop_name, c.field_name
FROM IrrigationSchedule s
JOIN Crops c ON c.id = s.crop_id
WHERE s.scheduled_date = CURDATE()
  AND s.status = 'pending';

-- View missed irrigations
SELECT * FROM IrrigationSchedule
WHERE status = 'missed'
ORDER BY scheduled_date DESC;
```

### Clear Schedules (if needed)
```sql
-- Clear all pending schedules for a crop
DELETE FROM IrrigationSchedule 
WHERE crop_id = 1 
  AND status = 'pending';

-- Clear all schedules for a crop (fresh start)
DELETE FROM IrrigationSchedule 
WHERE crop_id = 1;
```

### Statistics Queries
```sql
-- Get schedule statistics for a crop
SELECT 
    COUNT(*) as total,
    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
    SUM(CASE WHEN status = 'missed' THEN 1 ELSE 0 END) as missed,
    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
    ROUND(SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as adherence_rate
FROM IrrigationSchedule
WHERE crop_id = 1;
```

## Testing the System

### Step 1: Add a Crop
1. Go to "Recommend Crop"
2. Enter soil and weather data
3. Save crop with planting date (e.g., October 1st)

### Step 2: Generate Schedule
1. Go to "Irrigation Center"
2. Click "Full Schedule" for your crop
3. System generates complete schedule from planting to harvest

### Step 3: Mark Irrigation Complete
1. On schedule page, find today's irrigation
2. Click "Done" button
3. Confirm water amount used
4. Check that status changes to "Completed"

### Step 4: Test Missed Irrigation
1. Wait a day without marking irrigation
2. Refresh schedule page
3. System automatically marks yesterday as "Missed"
4. Warning appears with "Recalculate" button

### Step 5: Recalculate Schedule
1. Click "Recalculate" button
2. System regenerates future schedule
3. Adjusts for missed irrigation
4. May show "Urgent irrigation needed" if critical

## Benefits

1. **Complete Visibility**: See entire crop irrigation plan from day 1 to harvest
2. **Proactive Planning**: Know when irrigation is needed weeks in advance
3. **Accountability**: Track adherence to irrigation schedule
4. **Smart Adjustments**: Automatic recalculation when plans change
5. **Historical Record**: Complete irrigation history for analysis
6. **Water Optimization**: Prevent over/under irrigation
7. **Stage-Aware**: Different water needs for different growth stages

## Future Enhancements (Optional)

1. **Weather Integration**: Auto-skip irrigation when rain is forecasted
2. **SMS Reminders**: Send alerts for upcoming irrigations
3. **Soil Sensor Integration**: Auto-update moisture levels
4. **Multi-Field Management**: Bulk schedule generation
5. **Export Reports**: PDF/Excel export of schedules
6. **Mobile App**: Quick "I Irrigated" button on phone

## Summary

This upgrade transforms the irrigation system from a **reactive advice tool** to a **proactive lifecycle management system**, while keeping the existing "Today's Advice" feature fully functional. Farmers can now plan their entire crop irrigation from planting to harvest with intelligent recalculation when things don't go as planned.
