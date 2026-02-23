# Quick Reference Guide - Smart Farming System

## 🚀 Quick Start

### Start Application
```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Run application
python run.py

# Access at: http://localhost:5000
```

### Stop Application
```
Ctrl + C
```

---

## 📁 Important Files

### Configuration Files
| File | Purpose | Location |
|------|---------|----------|
| `.env` | Environment variables (DB, API keys) | Root directory |
| `app/config.py` | Application configuration | app/ |
| `requirements.txt` | Python dependencies | Root directory |

### Database Files
| File | Purpose | Location |
|------|---------|----------|
| `MYSQL_SETUP.md` | Database setup guide | Root directory |
| `DATABASE_ERD.md` | Complete ERD diagram | Root directory |
| `init_db.py` | SQLite initialization (legacy) | Root directory |

### Documentation Files
| File | Purpose | Location |
|------|---------|----------|
| `COMPLETE_PROJECT_DOCUMENTATION.md` | Full project docs | Root directory |
| `UI_STATE_SYNC_FIX.md` | State sync fix details | Root directory |
| `SOIL_MOISTURE_FIX.md` | Soil moisture fix details | Root directory |
| `IRRIGATION_SCHEDULE_UPGRADE.md` | Schedule feature docs | Root directory |

---

## 🗄️ Database Commands

### Connect to MySQL
```bash
mysql -u farming_user -p
# Password: farming_secure_password_2024
```

### Common Queries

#### View All Tables
```sql
USE smart_farming;
SHOW TABLES;
```

#### Check Recent Irrigation History
```sql
SELECT 
    ih.id,
    f.full_name,
    c.crop_name,
    ih.decision,
    ih.water_required,
    ih.recorded_at
FROM IrrigationHistory ih
JOIN Farmers f ON f.id = ih.farmer_id
JOIN Crops c ON c.id = ih.crop_id
ORDER BY ih.recorded_at DESC
LIMIT 10;
```

#### View Active Crops
```sql
SELECT 
    c.id,
    f.full_name,
    c.crop_name,
    c.field_name,
    c.planting_date,
    c.status
FROM Crops c
JOIN Farmers f ON f.id = c.farmer_id
WHERE c.status = 'active'
ORDER BY c.planting_date DESC;
```

#### Check Upcoming Irrigation Schedule
```sql
SELECT 
    s.scheduled_date,
    c.crop_name,
    c.field_name,
    s.water_amount,
    s.status
FROM IrrigationSchedule s
JOIN Crops c ON c.id = s.crop_id
WHERE s.status = 'pending'
  AND s.scheduled_date >= CURDATE()
ORDER BY s.scheduled_date
LIMIT 20;
```

#### Count Records by Table
```sql
SELECT 
    'Farmers' as table_name, COUNT(*) as count FROM Farmers
UNION ALL
SELECT 'Crops', COUNT(*) FROM Crops
UNION ALL
SELECT 'SoilRecords', COUNT(*) FROM SoilRecords
UNION ALL
SELECT 'IrrigationHistory', COUNT(*) FROM IrrigationHistory
UNION ALL
SELECT 'IrrigationSchedule', COUNT(*) FROM IrrigationSchedule;
```

#### Backup Database
```bash
# Full backup
mysqldump -u farming_user -p smart_farming > backup_$(date +%Y%m%d).sql

# Compressed backup
mysqldump -u farming_user -p smart_farming | gzip > backup_$(date +%Y%m%d).sql.gz
```

---

## 🌐 Key URLs

### Public Pages
- **Landing Page**: http://localhost:5000/
- **Login**: http://localhost:5000/auth/login
- **Register**: http://localhost:5000/auth/register

### Protected Pages (Login Required)
- **Dashboard**: http://localhost:5000/dashboard
- **Crop Recommendation**: http://localhost:5000/crops/recommend
- **My Crops**: http://localhost:5000/crops/my-crops
- **Irrigation Dashboard**: http://localhost:5000/irrigation/
- **Irrigation History**: http://localhost:5000/irrigation/history

### Dynamic URLs
- **Irrigation Advice**: http://localhost:5000/irrigation/{crop_id}
- **Full Schedule**: http://localhost:5000/irrigation/{crop_id}/schedule
- **Weekly Plan**: http://localhost:5000/irrigation/{crop_id}/weekly

---

## 📂 Project Structure

```
ecofriendly_anti/
├── app/
│   ├── models/          # Database CRUD operations
│   │   ├── farmer.py    # User management
│   │   ├── crop.py      # Crop management
│   │   ├── soil.py      # Soil records
│   │   ├── irrigation.py # Irrigation history
│   │   └── schedule.py  # Irrigation schedule
│   ├── routes/          # HTTP request handlers
│   │   ├── auth.py      # Login/Register
│   │   ├── main.py      # Dashboard
│   │   ├── crops.py     # Crop features
│   │   └── irrigation.py # Irrigation features
│   ├── services/        # Business logic
│   │   ├── weather.py   # Weather API
│   │   ├── ml_engine.py # ML predictions
│   │   ├── irrigation_engine.py # Calculations
│   │   └── advanced_scheduler.py # Full scheduling
│   ├── __init__.py      # Flask app factory
│   ├── config.py        # Configuration
│   └── database.py      # DB connection
├── templates/           # HTML templates
│   ├── auth/           # Login/Register pages
│   ├── main/           # Dashboard pages
│   ├── crops/          # Crop pages
│   └── irrigation/     # Irrigation pages
├── static/             # CSS, JS, images
├── models/             # ML model files (.pkl)
├── data/               # CSV datasets
└── .env                # Environment variables
```

---

## 🔧 Common Tasks

### Add New Farmer (Manual)
```sql
INSERT INTO Farmers (username, password_hash, full_name, location, phone, email)
VALUES ('testuser', 'pbkdf2:sha256:600000$hash', 'Test User', 'Hyderabad', '1234567890', 'test@example.com');
```

### Add New Crop (Manual)
```sql
INSERT INTO Crops (farmer_id, crop_name, field_name, planting_date, growth_duration, status)
VALUES (1, 'rice', 'North Field', '2026-02-01', 120, 'active');
```

### View Farmer's Complete Data
```sql
-- Replace farmer_id = 1 with actual ID
SELECT 'Crops' as type, COUNT(*) as count FROM Crops WHERE farmer_id = 1
UNION ALL
SELECT 'Soil Records', COUNT(*) FROM SoilRecords WHERE farmer_id = 1
UNION ALL
SELECT 'Irrigation History', COUNT(*) FROM IrrigationHistory WHERE farmer_id = 1
UNION ALL
SELECT 'Schedules', COUNT(*) FROM IrrigationSchedule WHERE farmer_id = 1;
```

### Clear Old Schedules
```sql
-- Delete completed schedules older than 60 days
DELETE FROM IrrigationSchedule
WHERE status IN ('completed', 'skipped')
  AND scheduled_date < DATE_SUB(CURDATE(), INTERVAL 60 DAY);
```

### Reset Farmer Password
```python
# In Python shell
from werkzeug.security import generate_password_hash
new_hash = generate_password_hash('new_password')
print(new_hash)
# Copy hash and update in database
```

```sql
UPDATE Farmers 
SET password_hash = 'pbkdf2:sha256:...' 
WHERE username = 'username';
```

---

## 🐛 Troubleshooting

### Issue: Can't Connect to Database
**Symptoms**: `Can't connect to MySQL server`

**Solutions**:
1. Check MySQL is running:
   ```bash
   # Windows
   net start MySQL80
   
   # Linux
   sudo systemctl status mysql
   ```

2. Verify credentials in `.env`:
   ```env
   DB_HOST=localhost
   DB_PORT=3306
   DB_NAME=smart_farming
   DB_USER=farming_user
   DB_PASSWORD=farming_secure_password_2024
   ```

3. Test connection:
   ```bash
   mysql -u farming_user -p
   ```

### Issue: Weather API Not Working
**Symptoms**: `Weather data not available`

**Solutions**:
1. Check API key in `.env`:
   ```env
   OPENWEATHER_API_KEY=your_actual_key_here
   ```

2. Verify API key is active at: https://home.openweathermap.org/api_keys

3. Check API quota (free tier: 60 calls/minute, 1000 calls/day)

4. Test API directly:
   ```bash
   curl "http://api.openweathermap.org/data/2.5/weather?q=Hyderabad&appid=YOUR_KEY"
   ```

### Issue: Module Not Found
**Symptoms**: `ModuleNotFoundError: No module named 'flask'`

**Solutions**:
1. Activate virtual environment:
   ```bash
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Verify installation:
   ```bash
   pip list
   ```

### Issue: Template Not Found
**Symptoms**: `TemplateNotFound: irrigation/advice.html`

**Solutions**:
1. Check file exists: `templates/irrigation/advice.html`
2. Check file name spelling (case-sensitive on Linux)
3. Restart Flask application
4. Clear browser cache

### Issue: Session Error
**Symptoms**: `RuntimeError: The session is unavailable`

**Solutions**:
1. Set SECRET_KEY in `.env`:
   ```env
   SECRET_KEY=your-secret-key-here-change-this-to-random-string
   ```

2. Generate secure key:
   ```python
   import secrets
   print(secrets.token_hex(32))
   ```

3. Restart application

### Issue: Port Already in Use
**Symptoms**: `Address already in use`

**Solutions**:
1. Find process using port 5000:
   ```bash
   # Windows
   netstat -ano | findstr :5000
   taskkill /PID <PID> /F
   
   # Linux
   lsof -i :5000
   kill -9 <PID>
   ```

2. Use different port:
   ```python
   # run.py
   app.run(port=5001)
   ```

---

## 🔑 Environment Variables Reference

### Required Variables
```env
# Flask
SECRET_KEY=generate-random-string-here
FLASK_ENV=development

# Database
DB_HOST=localhost
DB_PORT=3306
DB_NAME=smart_farming
DB_USER=farming_user
DB_PASSWORD=your-secure-password

# Weather API
OPENWEATHER_API_KEY=your-api-key-here
```

### Optional Variables
```env
# Debug mode (never use in production)
FLASK_DEBUG=True

# Custom port
FLASK_RUN_PORT=5000

# Custom host
FLASK_RUN_HOST=0.0.0.0
```

---

## 📊 Performance Tips

### Database Optimization
```sql
-- Check table sizes
SELECT 
    table_name,
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS "Size (MB)"
FROM information_schema.TABLES
WHERE table_schema = "smart_farming"
ORDER BY (data_length + index_length) DESC;

-- Analyze tables
ANALYZE TABLE Farmers, Crops, SoilRecords, IrrigationHistory, IrrigationSchedule;

-- Optimize tables
OPTIMIZE TABLE Farmers, Crops, SoilRecords, IrrigationHistory, IrrigationSchedule;
```

### Application Performance
- Use connection pooling for database
- Cache weather API responses (5-10 minutes)
- Implement pagination for large lists
- Use indexes on frequently queried columns
- Compress static assets

---

## 🔒 Security Checklist

### Production Deployment
- [ ] Change SECRET_KEY to strong random value
- [ ] Set FLASK_ENV=production
- [ ] Use strong database password
- [ ] Enable HTTPS
- [ ] Disable debug mode
- [ ] Implement rate limiting
- [ ] Setup firewall rules
- [ ] Regular security updates
- [ ] Automated backups
- [ ] Monitor logs for suspicious activity

---

## 📞 Support Resources

### Documentation
- [Complete Project Documentation](COMPLETE_PROJECT_DOCUMENTATION.md)
- [Database ERD](DATABASE_ERD.md)
- [MySQL Setup Guide](MYSQL_SETUP.md)
- [UI State Sync Fix](UI_STATE_SYNC_FIX.md)

### External Resources
- Flask Documentation: https://flask.palletsprojects.com/
- MySQL Documentation: https://dev.mysql.com/doc/
- OpenWeather API: https://openweathermap.org/api
- Bootstrap 5: https://getbootstrap.com/docs/5.3/

---

## 🎯 Quick Commands Cheat Sheet

```bash
# Start application
python run.py

# Install dependencies
pip install -r requirements.txt

# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Connect to MySQL
mysql -u farming_user -p

# Backup database
mysqldump -u farming_user -p smart_farming > backup.sql

# Restore database
mysql -u farming_user -p smart_farming < backup.sql

# Check Python version
python --version

# Check MySQL version
mysql --version

# List installed packages
pip list

# Generate secret key
python -c "import secrets; print(secrets.token_hex(32))"
```

---

**Last Updated**: February 22, 2026  
**Version**: 1.0.0
