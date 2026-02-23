# Database Commands Reference

## Quick Access to MySQL

```bash
# Login to MySQL
mysql -u farming_user -p
# Password: farming_secure_password_2024

# Or as root
mysql -u root -p
```

## Useful Queries

### View All Tables
```sql
USE smart_farming;
SHOW TABLES;
```

### Check Irrigation Schedules

```sql
-- View all schedules
SELECT 
    s.id,
    s.scheduled_date,
    c.crop_name,
    c.field_name,
    s.water_amount,
    s.status,
    s.reason
FROM IrrigationSchedule s
JOIN Crops c ON c.id = s.crop_id
ORDER BY s.scheduled_date DESC
LIMIT 20;

-- View today's pending irrigations
SELECT 
    s.*,
    c.crop_name,
    c.field_name,
    f.full_name as farmer_name
FROM IrrigationSchedule s
JOIN Crops c ON c.id = s.crop_id
JOIN Farmers f ON f.id = s.farmer_id
WHERE s.scheduled_date = CURDATE()
  AND s.status = 'pending';

-- View missed irrigations
SELECT 
    s.*,
    c.crop_name,
    c.field_name
FROM IrrigationSchedule s
JOIN Crops c ON c.id = s.crop_id
WHERE s.status = 'missed'
ORDER BY s.scheduled_date DESC;

-- Count schedules by status
SELECT 
    status,
    COUNT(*) as count
FROM IrrigationSchedule
GROUP BY status;
```

### Check Crops

```sql
-- View all active crops
SELECT 
    c.*,
    f.full_name as farmer_name,
    f.location
FROM Crops c
JOIN Farmers f ON f.id = c.farmer_id
WHERE c.status = 'active';

-- View crop with schedule count
SELECT 
    c.id,
    c.crop_name,
    c.field_name,
    c.planting_date,
    c.growth_duration,
    COUNT(s.id) as schedule_count
FROM Crops c
LEFT JOIN IrrigationSchedule s ON s.crop_id = c.id
WHERE c.status = 'active'
GROUP BY c.id;
```

### Check Irrigation History

```sql
-- Recent irrigation history
SELECT 
    h.*,
    c.crop_name,
    c.field_name
FROM IrrigationHistory h
JOIN Crops c ON c.id = h.crop_id
ORDER BY h.recorded_at DESC
LIMIT 20;

-- Total water used per crop
SELECT 
    c.crop_name,
    c.field_name,
    SUM(h.water_required) as total_water_mm,
    COUNT(h.id) as irrigation_count
FROM IrrigationHistory h
JOIN Crops c ON c.id = h.crop_id
GROUP BY c.id;
```

## Maintenance Commands

### Clear Old Schedules

```sql
-- Clear pending schedules for a specific crop
DELETE FROM IrrigationSchedule 
WHERE crop_id = 1 
  AND status = 'pending';

-- Clear all schedules for a crop (fresh start)
DELETE FROM IrrigationSchedule 
WHERE crop_id = 1;

-- Clear old completed schedules (older than 60 days)
DELETE FROM IrrigationSchedule
WHERE status IN ('completed', 'skipped')
  AND scheduled_date < DATE_SUB(CURDATE(), INTERVAL 60 DAY);
```

### Update Schedule Status

```sql
-- Mark a schedule as completed
UPDATE IrrigationSchedule
SET status = 'completed',
    completed_at = NOW()
WHERE id = 1;

-- Mark overdue schedules as missed
UPDATE IrrigationSchedule
SET status = 'missed'
WHERE scheduled_date < CURDATE()
  AND status = 'pending';

-- Skip irrigation due to rain
UPDATE IrrigationSchedule
SET status = 'skipped',
    reason = 'Skipped due to rainfall'
WHERE id = 1;
```

### Statistics Queries

```sql
-- Schedule adherence rate for a crop
SELECT 
    c.crop_name,
    COUNT(*) as total_schedules,
    SUM(CASE WHEN s.status = 'completed' THEN 1 ELSE 0 END) as completed,
    SUM(CASE WHEN s.status = 'missed' THEN 1 ELSE 0 END) as missed,
    ROUND(
        SUM(CASE WHEN s.status = 'completed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
        1
    ) as adherence_rate
FROM IrrigationSchedule s
JOIN Crops c ON c.id = s.crop_id
WHERE c.id = 1
GROUP BY c.id;

-- Farmer's overall irrigation performance
SELECT 
    f.full_name,
    COUNT(s.id) as total_schedules,
    SUM(CASE WHEN s.status = 'completed' THEN 1 ELSE 0 END) as completed,
    SUM(CASE WHEN s.status = 'missed' THEN 1 ELSE 0 END) as missed,
    ROUND(
        SUM(CASE WHEN s.status = 'completed' THEN 1 ELSE 0 END) * 100.0 / COUNT(s.id),
        1
    ) as adherence_rate
FROM Farmers f
JOIN IrrigationSchedule s ON s.farmer_id = f.id
WHERE f.id = 1
GROUP BY f.id;
```

## Troubleshooting

### Reset Everything for a Crop

```sql
-- Complete reset (use with caution!)
DELETE FROM IrrigationSchedule WHERE crop_id = 1;
DELETE FROM IrrigationHistory WHERE crop_id = 1;
DELETE FROM SoilRecords WHERE crop_id = 1;
-- Then regenerate schedule from the app
```

### Check for Duplicate Schedules

```sql
-- Find duplicate schedules (shouldn't exist due to UNIQUE constraint)
SELECT 
    crop_id,
    scheduled_date,
    COUNT(*) as count
FROM IrrigationSchedule
GROUP BY crop_id, scheduled_date
HAVING COUNT(*) > 1;
```

### View Schedule Gaps

```sql
-- Find days without scheduled irrigation
SELECT 
    DATE_ADD(c.planting_date, INTERVAL seq.n DAY) as missing_date
FROM Crops c
CROSS JOIN (
    SELECT 0 as n UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 
    UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9
) seq
WHERE c.id = 1
  AND DATE_ADD(c.planting_date, INTERVAL seq.n DAY) <= DATE_ADD(c.planting_date, INTERVAL c.growth_duration DAY)
  AND DATE_ADD(c.planting_date, INTERVAL seq.n DAY) NOT IN (
      SELECT scheduled_date 
      FROM IrrigationSchedule 
      WHERE crop_id = 1
  )
LIMIT 20;
```

## Backup Commands

### Backup Specific Tables

```bash
# Backup irrigation schedules
mysqldump -u farming_user -p smart_farming IrrigationSchedule > irrigation_schedule_backup.sql

# Backup all irrigation-related tables
mysqldump -u farming_user -p smart_farming IrrigationSchedule IrrigationHistory > irrigation_backup.sql

# Backup entire database
mysqldump -u farming_user -p smart_farming > smart_farming_backup.sql
```

### Restore from Backup

```bash
# Restore specific table
mysql -u farming_user -p smart_farming < irrigation_schedule_backup.sql

# Restore entire database
mysql -u farming_user -p smart_farming < smart_farming_backup.sql
```

## Performance Optimization

### Check Index Usage

```sql
-- Show indexes on IrrigationSchedule
SHOW INDEX FROM IrrigationSchedule;

-- Analyze table
ANALYZE TABLE IrrigationSchedule;
```

### Query Performance

```sql
-- Explain query execution plan
EXPLAIN SELECT * FROM IrrigationSchedule 
WHERE crop_id = 1 
  AND scheduled_date >= CURDATE()
  AND status = 'pending';
```

## Exit MySQL

```sql
EXIT;
```

## Quick Reference Card

| Task | Command |
|------|---------|
| Login | `mysql -u farming_user -p` |
| Use Database | `USE smart_farming;` |
| Show Tables | `SHOW TABLES;` |
| View Schedules | `SELECT * FROM IrrigationSchedule ORDER BY scheduled_date;` |
| Today's Tasks | `SELECT * FROM IrrigationSchedule WHERE scheduled_date = CURDATE();` |
| Clear Pending | `DELETE FROM IrrigationSchedule WHERE status = 'pending';` |
| Mark Complete | `UPDATE IrrigationSchedule SET status = 'completed' WHERE id = X;` |
| Exit | `EXIT;` |
