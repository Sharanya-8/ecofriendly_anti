# Complete Entity Relationship Diagram (ERD)

## Database Schema Overview

**Database Name:** `smart_farming`  
**Database Type:** MySQL 8.0+  
**Character Set:** utf8mb4  
**Collation:** utf8mb4_unicode_ci

---

## Entity Relationship Diagram (Visual)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SMART FARMING DATABASE SCHEMA                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────┐
│       Farmers            │
│ ──────────────────────── │
│ PK  id (INT)             │◄──────────┐
│ UK  username (VARCHAR)   │           │
│     password_hash (TEXT) │           │
│     full_name (VARCHAR)  │           │
│     location (VARCHAR)   │           │
│     phone (VARCHAR)      │           │
│     email (VARCHAR)      │           │
│     created_at (TIMESTAMP)│          │
│     last_login (TIMESTAMP)│          │
└──────────────────────────┘           │
                                       │ 1:N
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
                    │                  │                  │
         ┌──────────▼──────────┐  ┌───▼──────────────┐  │
         │      Crops          │  │  SoilRecords     │  │
         │ ─────────────────── │  │ ──────────────── │  │
         │ PK  id (INT)        │  │ PK  id (INT)     │  │
         │ FK  farmer_id (INT) │  │ FK  farmer_id    │  │
         │     crop_name (VAR) │  │ FK  crop_id (INT)│◄─┤
         │     field_name (VAR)│  │     N (DECIMAL)  │  │
         │     planting_date   │  │     P (DECIMAL)  │  │
         │     growth_duration │  │     K (DECIMAL)  │  │
         │     status (ENUM)   │  │     ph (DECIMAL) │  │
         │     created_at      │  │     moisture (DEC)│ │
         │     updated_at      │  │     sand (DECIMAL)│ │
         └──────────┬──────────┘  │     clay (DECIMAL)│ │
                    │             │     soil_fertility│ │
                    │             │     recorded_at   │ │
                    │             └───────────────────┘ │
                    │ 1:N                               │
                    │                                   │
         ┌──────────┼───────────────────────────────────┘
         │          │
         │          │
    ┌────▼──────────▼─────┐      ┌──────────────────────┐
    │ IrrigationHistory   │      │ IrrigationSchedule   │
    │ ─────────────────── │      │ ──────────────────── │
    │ PK  id (INT)        │      │ PK  id (INT)         │
    │ FK  farmer_id (INT) │      │ FK  farmer_id (INT)  │
    │ FK  crop_id (INT)   │      │ FK  crop_id (INT)    │
    │     city (VARCHAR)  │      │     scheduled_date   │
    │     stage (VARCHAR) │      │     water_amount     │
    │     days_after_sow  │      │     status (ENUM)    │
    │     et0 (DECIMAL)   │      │     reason (TEXT)    │
    │     kc (DECIMAL)    │      │     completed_at     │
    │     water_required  │      │     created_at       │
    │     decision (TEXT) │      │     updated_at       │
    │     recorded_at     │      └──────────────────────┘
    └─────────────────────┘

Legend:
  PK = Primary Key
  FK = Foreign Key
  UK = Unique Key
  1:N = One-to-Many Relationship
```

---

## Detailed Table Specifications

### 1. Farmers Table
**Purpose:** Store user accounts for farmers

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | Unique farmer identifier |
| username | VARCHAR(100) | UNIQUE, NOT NULL | Login username (lowercase) |
| password_hash | VARCHAR(255) | NOT NULL | Hashed password (Werkzeug) |
| full_name | VARCHAR(200) | NOT NULL | Farmer's full name |
| location | VARCHAR(100) | | Primary district/city |
| phone | VARCHAR(20) | | Contact phone number |
| email | VARCHAR(150) | | Email address |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Account creation time |
| last_login | TIMESTAMP | NULL | Last login timestamp |

**Indexes:**
- `idx_username` on `username`

**Relationships:**
- One farmer → Many crops (1:N)
- One farmer → Many soil records (1:N)
- One farmer → Many irrigation history records (1:N)
- One farmer → Many irrigation schedules (1:N)

---

### 2. Crops Table
**Purpose:** Store crop information for each farmer

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | Unique crop identifier |
| farmer_id | INT | FOREIGN KEY → Farmers(id), NOT NULL | Owner farmer |
| crop_name | VARCHAR(100) | NOT NULL | Crop type (e.g., rice, wheat) |
| field_name | VARCHAR(150) | NOT NULL | Field/plot name |
| planting_date | DATE | NOT NULL | Date crop was planted |
| growth_duration | INT | NOT NULL | Total growth days (e.g., 120) |
| status | ENUM | 'active', 'harvested', 'failed' | Current crop status |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation time |
| updated_at | TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP | Last update time |

**Indexes:**
- `idx_farmer_status` on `(farmer_id, status)`
- `idx_planting_date` on `planting_date`

**Relationships:**
- Many crops → One farmer (N:1)
- One crop → Many soil records (1:N)
- One crop → Many irrigation history records (1:N)
- One crop → Many irrigation schedules (1:N)

**Cascade Rules:**
- ON DELETE CASCADE: Deleting farmer deletes all their crops
- Deleting crop deletes all related irrigation history and schedules

---

### 3. SoilRecords Table
**Purpose:** Store soil test results and readings

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | Unique record identifier |
| farmer_id | INT | FOREIGN KEY → Farmers(id), NOT NULL | Owner farmer |
| crop_id | INT | FOREIGN KEY → Crops(id), NULL | Associated crop (optional) |
| N | DECIMAL(8,2) | NOT NULL | Nitrogen content (kg/ha) |
| P | DECIMAL(8,2) | NOT NULL | Phosphorus content (kg/ha) |
| K | DECIMAL(8,2) | NOT NULL | Potassium content (kg/ha) |
| ph | DECIMAL(4,2) | NOT NULL | Soil pH level (0-14) |
| moisture | DECIMAL(5,2) | NOT NULL | Soil moisture percentage (0-100) |
| sand | DECIMAL(5,2) | | Sand percentage |
| clay | DECIMAL(5,2) | | Clay percentage |
| soil_fertility | VARCHAR(50) | | Fertility classification |
| recorded_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Reading timestamp |

**Indexes:**
- `idx_farmer_date` on `(farmer_id, recorded_at)`
- `idx_crop` on `crop_id`

**Relationships:**
- Many soil records → One farmer (N:1)
- Many soil records → One crop (N:1, optional)

**Cascade Rules:**
- ON DELETE CASCADE: Deleting farmer deletes all their soil records
- ON DELETE SET NULL: Deleting crop sets crop_id to NULL

---

### 4. IrrigationHistory Table
**Purpose:** Store past irrigation calculations and decisions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | Unique record identifier |
| farmer_id | INT | FOREIGN KEY → Farmers(id), NOT NULL | Owner farmer |
| crop_id | INT | FOREIGN KEY → Crops(id), NOT NULL | Associated crop |
| city | VARCHAR(100) | | Location for weather data |
| stage | VARCHAR(50) | | Growth stage (Initial, Development, etc.) |
| days_after_sowing | INT | | Days since planting |
| et0 | DECIMAL(8,3) | | Reference evapotranspiration (mm/day) |
| kc | DECIMAL(5,3) | | Crop coefficient |
| water_required | DECIMAL(10,3) | | Calculated water need (mm) |
| decision | TEXT | | Irrigation recommendation |
| recorded_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Calculation timestamp |

**Indexes:**
- `idx_farmer_date` on `(farmer_id, recorded_at)`
- `idx_crop_date` on `(crop_id, recorded_at)`

**Relationships:**
- Many irrigation records → One farmer (N:1)
- Many irrigation records → One crop (N:1)

**Cascade Rules:**
- ON DELETE CASCADE: Deleting farmer or crop deletes all related history

---

### 5. IrrigationSchedule Table
**Purpose:** Store future irrigation schedule (full lifecycle)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | Unique schedule identifier |
| farmer_id | INT | FOREIGN KEY → Farmers(id), NOT NULL | Owner farmer |
| crop_id | INT | FOREIGN KEY → Crops(id), NOT NULL | Associated crop |
| scheduled_date | DATE | NOT NULL | Planned irrigation date |
| water_amount | DECIMAL(10,3) | NOT NULL | Planned water amount (mm) |
| status | ENUM | 'pending', 'completed', 'missed', 'skipped' | Schedule status |
| reason | TEXT | | Reason for skip/miss |
| completed_at | TIMESTAMP | NULL | Actual completion time |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Schedule creation time |
| updated_at | TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP | Last update time |

**Indexes:**
- `idx_farmer_date` on `(farmer_id, scheduled_date)`
- `idx_crop_status` on `(crop_id, status)`
- `idx_scheduled_date` on `scheduled_date`

**Unique Constraints:**
- `unique_crop_date` on `(crop_id, scheduled_date)` - One schedule per crop per day

**Relationships:**
- Many schedules → One farmer (N:1)
- Many schedules → One crop (N:1)

**Cascade Rules:**
- ON DELETE CASCADE: Deleting farmer or crop deletes all related schedules

---

## Relationship Summary

### One-to-Many Relationships

1. **Farmers → Crops** (1:N)
   - One farmer can have multiple crops
   - Each crop belongs to exactly one farmer
   - Cascade: Delete farmer → Delete all crops

2. **Farmers → SoilRecords** (1:N)
   - One farmer can have multiple soil readings
   - Each soil record belongs to exactly one farmer
   - Cascade: Delete farmer → Delete all soil records

3. **Farmers → IrrigationHistory** (1:N)
   - One farmer can have multiple irrigation records
   - Each record belongs to exactly one farmer
   - Cascade: Delete farmer → Delete all history

4. **Farmers → IrrigationSchedule** (1:N)
   - One farmer can have multiple scheduled irrigations
   - Each schedule belongs to exactly one farmer
   - Cascade: Delete farmer → Delete all schedules

5. **Crops → SoilRecords** (1:N, Optional)
   - One crop can have multiple soil readings
   - Each soil record can optionally link to a crop
   - Cascade: Delete crop → Set crop_id to NULL

6. **Crops → IrrigationHistory** (1:N)
   - One crop can have multiple irrigation records
   - Each record belongs to exactly one crop
   - Cascade: Delete crop → Delete all history

7. **Crops → IrrigationSchedule** (1:N)
   - One crop can have multiple scheduled irrigations
   - Each schedule belongs to exactly one crop
   - Cascade: Delete crop → Delete all schedules

---

## Data Flow Diagram

```
┌─────────────┐
│   Farmer    │
│  Registers  │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌──────────────┐
│   Adds      │────►│  SoilRecords │
│   Crop      │     │  (Optional)  │
└──────┬──────┘     └──────────────┘
       │
       ▼
┌─────────────────────────────────┐
│  Irrigation Recommendation      │
│  (Uses: Weather + Soil + Stage) │
└──────┬──────────────────────────┘
       │
       ├──────────────┬─────────────────┐
       ▼              ▼                 ▼
┌──────────────┐ ┌─────────────┐ ┌──────────────┐
│ Irrigation   │ │ Irrigation  │ │   Weekly     │
│   History    │ │  Schedule   │ │   Forecast   │
│  (Past)      │ │  (Future)   │ │  (5 days)    │
└──────────────┘ └─────────────┘ └──────────────┘
```

---

## Key Constraints and Business Rules

### 1. User Authentication
- Username must be unique (case-insensitive)
- Password stored as hash (Werkzeug PBKDF2)
- Last login tracked automatically

### 2. Crop Management
- Status: active, harvested, failed
- Growth duration: Typically 60-180 days
- Planting date: Cannot be in future
- One farmer can have multiple active crops

### 3. Soil Records
- NPK values: Typically 0-300 kg/ha
- pH: Range 0-14 (optimal 6-7.5)
- Moisture: Percentage 0-100%
- Can exist without crop (general field reading)

### 4. Irrigation History
- Records every calculation made
- Includes weather conditions at time
- Tracks growth stage and Kc value
- Immutable (historical record)

### 5. Irrigation Schedule
- Generated for full crop lifecycle
- One entry per crop per date (unique constraint)
- Status transitions: pending → completed/missed/skipped
- Missed detection: Past dates with pending status
- Can be regenerated with new soil moisture

---

## Database Size Estimates

### Per Farmer (Annual)
- Crops: 2-5 records
- Soil Records: 10-20 records
- Irrigation History: 50-100 records
- Irrigation Schedule: 200-600 records (2-5 crops × 120 days)

### Storage Requirements
- Small farm (100 farmers): ~50 MB/year
- Medium farm (1000 farmers): ~500 MB/year
- Large farm (10000 farmers): ~5 GB/year

---

## Backup and Maintenance

### Recommended Backup Schedule
```sql
-- Daily backup
mysqldump -u farming_user -p smart_farming > backup_$(date +%Y%m%d).sql

-- Weekly full backup with compression
mysqldump -u farming_user -p smart_farming | gzip > backup_$(date +%Y%m%d).sql.gz
```

### Cleanup Old Data
```sql
-- Delete completed schedules older than 60 days
DELETE FROM IrrigationSchedule 
WHERE status IN ('completed', 'skipped') 
  AND scheduled_date < DATE_SUB(CURDATE(), INTERVAL 60 DAY);

-- Archive old irrigation history (older than 1 year)
CREATE TABLE IrrigationHistory_Archive LIKE IrrigationHistory;
INSERT INTO IrrigationHistory_Archive 
SELECT * FROM IrrigationHistory 
WHERE recorded_at < DATE_SUB(NOW(), INTERVAL 1 YEAR);
```

---

## Performance Optimization

### Index Strategy
All foreign keys are indexed for fast joins:
- `farmer_id` columns: Fast farmer-specific queries
- `crop_id` columns: Fast crop-specific queries
- Date columns: Fast time-range queries
- Composite indexes: Optimized for common query patterns

### Query Optimization Tips
```sql
-- Good: Uses index
SELECT * FROM Crops WHERE farmer_id = 1 AND status = 'active';

-- Good: Uses composite index
SELECT * FROM IrrigationHistory 
WHERE farmer_id = 1 AND recorded_at > '2026-01-01';

-- Avoid: Full table scan
SELECT * FROM IrrigationHistory WHERE decision LIKE '%urgent%';
```

---

## Security Considerations

1. **Password Security**
   - Hashed using Werkzeug (PBKDF2-SHA256)
   - Never store plain text passwords
   - Minimum 8 characters recommended

2. **SQL Injection Prevention**
   - All queries use parameterized statements
   - PyMySQL handles escaping automatically

3. **Access Control**
   - Farmers can only access their own data
   - All queries include `farmer_id` check
   - Foreign key constraints enforce data integrity

4. **Database User Permissions**
   - Application user: SELECT, INSERT, UPDATE, DELETE only
   - No DROP, CREATE, ALTER permissions
   - Separate admin user for schema changes

---

## Migration from SQLite to MySQL

If migrating from SQLite:

```bash
# Export from SQLite
sqlite3 farming.db .dump > sqlite_dump.sql

# Convert to MySQL format (manual adjustments needed)
# - Change AUTOINCREMENT to AUTO_INCREMENT
# - Change TEXT to VARCHAR with length
# - Change datetime('now','localtime') to CURRENT_TIMESTAMP
# - Add ENGINE=InnoDB

# Import to MySQL
mysql -u farming_user -p smart_farming < mysql_converted.sql
```

---

## Entity Relationship Summary

```
Farmers (1) ──────────────────────────────────────────────────────┐
   │                                                               │
   │ 1:N                                                           │
   │                                                               │
   ├──► Crops (N)                                                  │
   │      │                                                        │
   │      │ 1:N                                                    │
   │      │                                                        │
   │      ├──► IrrigationHistory (N)                              │
   │      │                                                        │
   │      ├──► IrrigationSchedule (N)                             │
   │      │                                                        │
   │      └──► SoilRecords (N) ◄──────────────────────────────────┤
   │                                                               │
   └──► SoilRecords (N) (without crop_id)                         │
   └──► IrrigationHistory (N) ◄──────────────────────────────────┘
   └──► IrrigationSchedule (N) ◄──────────────────────────────────┘
```

**Total Tables:** 5  
**Total Relationships:** 8 (all 1:N)  
**Total Indexes:** 12  
**Total Unique Constraints:** 2

