# 🌾 Smart Farming Irrigation System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)](https://flask.palletsprojects.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)](https://www.mysql.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An AI-powered web application that helps farmers optimize water usage through intelligent irrigation recommendations based on real-time weather data, soil conditions, and crop growth stages.

![Smart Farming Banner](https://via.placeholder.com/1200x300/4CAF50/FFFFFF?text=Smart+Farming+Irrigation+System)

---

## 📋 Table of Contents

- [Features](#-features)
- [Demo](#-demo)
- [Technology Stack](#-technology-stack)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Database Schema](#-database-schema)
- [Machine Learning Models](#-machine-learning-models)
- [Screenshots](#-screenshots)
- [Contributing](#-contributing)
- [Troubleshooting](#-troubleshooting)
- [License](#-license)
- [Contact](#-contact)

---

## ✨ Features

### 🌱 Core Features
- **User Authentication** - Secure registration and login system
- **Crop Management** - Add and manage multiple crops with ML-based recommendations
- **Smart Irrigation** - Real-time irrigation advice based on weather and soil conditions
- **Full Lifecycle Scheduling** - Complete irrigation plan from planting to harvest
- **Weather Integration** - Real-time weather data with GPS location support
- **Dashboard Analytics** - Track water savings and irrigation history

### 🤖 AI/ML Features
- **Crop Recommendation** - ML model suggests best crops based on soil parameters
- **Soil Fertility Prediction** - Classify soil fertility (Low/Medium/High)
- **Growth Stage Detection** - Automatic detection of 4 FAO-56 crop growth stages
- **ET₀ Calculation** - Penman-Monteith evapotranspiration calculation

### 📊 Advanced Features
- **Daily Moisture Simulation** - Track soil moisture changes over time
- **Missed Irrigation Detection** - Automatic detection and alerts
- **Dynamic Recalculation** - Adjust schedule based on actual conditions
- **5-Day Forecast** - Weekly irrigation planning with weather forecast
- **Live GPS Location** - Get weather data using device location

---

## 🎥 Demo

### Live Demo
🔗 [Demo Link](http://your-demo-url.com) *(Coming Soon)*

### Quick Start Video
📹 [Watch Tutorial](http://your-video-url.com) *(Coming Soon)*

---

## 🛠️ Technology Stack

### Backend
- **Framework**: Flask 2.3+
- **Language**: Python 3.8+
- **Database**: MySQL 8.0+
- **ORM**: PyMySQL (Raw SQL with dict cursors)
- **Authentication**: Werkzeug Security (PBKDF2-SHA256)

### Frontend
- **Template Engine**: Jinja2
- **CSS Framework**: Bootstrap 5.3
- **Icons**: Bootstrap Icons
- **JavaScript**: Vanilla JS + Geolocation API

### Machine Learning
- **Framework**: scikit-learn
- **Models**: Random Forest Classifier
- **Storage**: Pickle files

### External APIs
- **Weather**: OpenWeatherMap API
- **Geocoding**: OpenWeatherMap Geocoding API

---

## 📦 Installation

### Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8 or higher
- MySQL 8.0 or higher
- pip (Python package manager)
- Git (optional)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/smart-farming-irrigation.git
cd smart-farming-irrigation
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Setup MySQL Database

1. **Install MySQL** (if not already installed)
   - Windows: Download from [MySQL Downloads](https://dev.mysql.com/downloads/installer/)
   - Linux: `sudo apt install mysql-server`
   - Mac: `brew install mysql`

2. **Create Database and User**

```bash
mysql -u root -p
```

```sql
-- Create database
CREATE DATABASE smart_farming CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user
CREATE USER 'farming_user'@'localhost' IDENTIFIED BY 'farming_secure_password_2024';

-- Grant privileges
GRANT ALL PRIVILEGES ON smart_farming.* TO 'farming_user'@'localhost';
FLUSH PRIVILEGES;

-- Use database
USE smart_farming;
```

3. **Create Tables**

Run the SQL commands from [MYSQL_SETUP.md](MYSQL_SETUP.md) to create all tables.

### Step 5: Configure Environment Variables

Create a `.env` file in the root directory:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-change-this-to-random-string
FLASK_ENV=development

# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_NAME=smart_farming
DB_USER=farming_user
DB_PASSWORD=farming_secure_password_2024

# Weather API Configuration
OPENWEATHER_API_KEY=your-openweather-api-key-here
```

**Generate a secure SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**Get OpenWeather API Key:**
1. Sign up at [OpenWeatherMap](https://openweathermap.org/api)
2. Get your free API key from the dashboard
3. Add it to `.env` file

### Step 6: Run the Application

```bash
python run.py
```

The application will be available at: **http://localhost:5000**

---

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `SECRET_KEY` | Flask session encryption key | Yes | - |
| `FLASK_ENV` | Environment mode (development/production) | No | production |
| `DB_HOST` | MySQL host address | Yes | localhost |
| `DB_PORT` | MySQL port number | Yes | 3306 |
| `DB_NAME` | Database name | Yes | smart_farming |
| `DB_USER` | Database username | Yes | farming_user |
| `DB_PASSWORD` | Database password | Yes | - |
| `OPENWEATHER_API_KEY` | OpenWeather API key | Yes | - |

### Application Settings

Edit `app/config.py` to customize application settings:

```python
class Config:
    # Session timeout (in minutes)
    PERMANENT_SESSION_LIFETIME = 60
    
    # Maximum file upload size (in bytes)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # Weather API cache duration (in seconds)
    WEATHER_CACHE_DURATION = 300  # 5 minutes
```

---

## 🚀 Usage

### For Farmers

#### 1. Register an Account
1. Navigate to http://localhost:5000
2. Click "Register"
3. Fill in your details (username, password, full name, location)
4. Click "Create Account"

#### 2. Get Crop Recommendation
1. Login to your dashboard
2. Click "Get Crop Recommendation"
3. Enter your soil test results:
   - Nitrogen (N)
   - Phosphorus (P)
   - Potassium (K)
   - pH level
   - Soil moisture
   - Sand percentage
   - Clay percentage
4. Click 📍 for live location or enter district manually
5. Get ML-based crop recommendation
6. Confirm and add crop with planting date

#### 3. Get Irrigation Advice
1. Go to "Irrigation Center" from dashboard
2. Select your crop
3. Enter current soil moisture percentage
4. Click "Calculate & Save"
5. View recommendation:
   - ✅ No irrigation needed
   - ⚠️ Light irrigation recommended
   - 🚨 Urgent irrigation required

#### 4. View Full Irrigation Schedule
1. From irrigation page, click "View Full Schedule"
2. See complete irrigation plan (planting to harvest)
3. View daily breakdown with:
   - Date
   - Growth stage
   - Water requirement
   - Status (Pending/Completed/Missed)
4. Mark irrigations as completed
5. Regenerate schedule with new soil moisture if needed

#### 5. Track Your Progress
1. View "Irrigation History" for past events
2. Check dashboard for:
   - Active crops count
   - Total irrigations
   - Water savings
   - Upcoming schedule

### For Developers

#### Project Structure
```
ecofriendly_anti/
├── app/
│   ├── models/              # Database CRUD operations
│   ├── routes/              # HTTP request handlers
│   ├── services/            # Business logic
│   ├── __init__.py          # Flask app factory
│   ├── config.py            # Configuration
│   └── database.py          # Database connection
├── templates/               # HTML templates
├── static/                  # CSS, JS, images
├── models/                  # ML model files
├── data/                    # CSV datasets
├── .env                     # Environment variables
├── requirements.txt         # Python dependencies
└── run.py                   # Application entry point
```

#### Adding New Features

**Add a new route:**
```python
# app/routes/new_feature.py
from flask import Blueprint, render_template

new_bp = Blueprint("new_feature", __name__, url_prefix="/new")

@new_bp.route("/")
def index():
    return render_template("new_feature/index.html")

# Register in app/__init__.py
from app.routes.new_feature import new_bp
app.register_blueprint(new_bp)
```

**Add a new model:**
```python
# app/models/new_model.py
from app.database import query_db, execute_db

def create_record(data):
    return execute_db(
        "INSERT INTO TableName (col1, col2) VALUES (%s, %s)",
        (data["col1"], data["col2"])
    )
```

---

## 📡 API Documentation

### Authentication Endpoints

#### Register User
```http
POST /auth/register
Content-Type: application/x-www-form-urlencoded

username=farmer1&password=secure123&full_name=John Doe&location=Hyderabad
```

#### Login
```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=farmer1&password=secure123
```

### Irrigation Endpoints

#### Get Today's Irrigation Advice
```http
GET /irrigation/<crop_id>
```

#### Calculate Irrigation
```http
POST /irrigation/<crop_id>
Content-Type: application/x-www-form-urlencoded

soil_moisture=45.5
```

#### Generate Full Schedule
```http
POST /irrigation/<crop_id>/schedule/generate
Content-Type: application/x-www-form-urlencoded

soil_moisture=50.0
```

#### Get Weather by GPS
```http
POST /irrigation/weather/live
Content-Type: application/json

{
  "latitude": 17.385,
  "longitude": 78.4867
}
```

**Response:**
```json
{
  "success": true,
  "weather": {
    "temp": 28.5,
    "humidity": 65,
    "rain": 0,
    "desc": "Clear sky"
  }
}
```

For complete API documentation, see [COMPLETE_PROJECT_DOCUMENTATION.md](COMPLETE_PROJECT_DOCUMENTATION.md).

---

## 🗄️ Database Schema

### Tables Overview

| Table | Purpose | Records/Year |
|-------|---------|--------------|
| Farmers | User accounts | 1 per farmer |
| Crops | Crop information | 2-5 per farmer |
| SoilRecords | Soil test results | 10-20 per farmer |
| IrrigationHistory | Past irrigation events | 50-100 per farmer |
| IrrigationSchedule | Future irrigation plan | 200-600 per farmer |

### Entity Relationships

```
Farmers (1) ──┬──► Crops (N)
              │      ├──► IrrigationHistory (N)
              │      ├──► IrrigationSchedule (N)
              │      └──► SoilRecords (N)
              │
              ├──► SoilRecords (N)
              ├──► IrrigationHistory (N)
              └──► IrrigationSchedule (N)
```

For complete ERD, see [DATABASE_ERD.md](DATABASE_ERD.md).

---

## 🤖 Machine Learning Models

### 1. Crop Recommendation Model

**File**: `models/crop_model.pkl`  
**Algorithm**: Random Forest Classifier  
**Accuracy**: ~99%

**Input Features** (7):
- N (Nitrogen): 0-140 kg/ha
- P (Phosphorus): 5-145 kg/ha
- K (Potassium): 5-205 kg/ha
- pH: 3.5-9.9
- Rainfall: 20-300 mm
- Temperature: 8-43°C
- Humidity: 14-100%

**Output**: Crop name (22 classes)

**Supported Crops**:
rice, maize, chickpea, kidneybeans, pigeonpeas, mothbeans, mungbean, blackgram, lentil, pomegranate, banana, mango, grapes, watermelon, muskmelon, apple, orange, papaya, coconut, cotton, jute, coffee

### 2. Soil Fertility Model

**File**: `models/soil_model.pkl`  
**Algorithm**: Random Forest Classifier

**Input Features** (7):
- N, P, K, pH, Sand %, Clay %, Moisture %

**Output**: Fertility class (Low/Medium/High)

---

## 📸 Screenshots

### Landing Page
![Landing Page](https://via.placeholder.com/800x400/4CAF50/FFFFFF?text=Landing+Page)

### Dashboard
![Dashboard](https://via.placeholder.com/800x400/2196F3/FFFFFF?text=Dashboard)

### Crop Recommendation
![Crop Recommendation](https://via.placeholder.com/800x400/FF9800/FFFFFF?text=Crop+Recommendation)

### Irrigation Schedule
![Irrigation Schedule](https://via.placeholder.com/800x400/9C27B0/FFFFFF?text=Irrigation+Schedule)

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### How to Contribute

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit your changes**
   ```bash
   git commit -m "Add amazing feature"
   ```
4. **Push to the branch**
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Open a Pull Request**

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable names
- Add docstrings to functions
- Comment complex logic
- Write unit tests for new features

### Commit Message Format

```
feat: Add new irrigation algorithm
fix: Resolve weather API timeout issue
docs: Update installation guide
refactor: Simplify schedule generation
test: Add unit tests for irrigation engine
```

---

## 🐛 Troubleshooting

### Common Issues

#### Issue: Can't connect to MySQL
**Error**: `Can't connect to MySQL server`

**Solution**:
```bash
# Check MySQL is running
# Windows
net start MySQL80

# Linux
sudo systemctl status mysql

# Verify credentials in .env
mysql -u farming_user -p
```

#### Issue: Weather API not working
**Error**: `Weather data not available`

**Solution**:
1. Check API key in `.env`
2. Verify API quota at https://home.openweathermap.org/api_keys
3. Free tier: 60 calls/minute, 1000 calls/day

#### Issue: Module not found
**Error**: `ModuleNotFoundError: No module named 'flask'`

**Solution**:
```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

#### Issue: Port already in use
**Error**: `Address already in use`

**Solution**:
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux
lsof -i :5000
kill -9 <PID>
```

For more troubleshooting, see [QUICK_REFERENCE.md](QUICK_REFERENCE.md).

---

## 📚 Documentation

### Complete Documentation
- [Complete Project Documentation](COMPLETE_PROJECT_DOCUMENTATION.md) - Full technical documentation
- [Database ERD](DATABASE_ERD.md) - Complete database schema and relationships
- [Quick Reference](QUICK_REFERENCE.md) - Quick commands and tips
- [Project Summary](PROJECT_SUMMARY.md) - Executive summary

### Setup Guides
- [MySQL Setup](MYSQL_SETUP.md) - Database setup guide
- [Quick Start Irrigation](QUICK_START_IRRIGATION.md) - Irrigation feature guide

### Feature Documentation
- [Irrigation Schedule Upgrade](IRRIGATION_SCHEDULE_UPGRADE.md) - Full lifecycle scheduling
- [Soil Moisture Fix](SOIL_MOISTURE_FIX.md) - Dynamic moisture update
- [UI State Sync Fix](UI_STATE_SYNC_FIX.md) - State synchronization

---

## 🔒 Security

### Security Features
- Password hashing using PBKDF2-SHA256
- Session-based authentication
- SQL injection prevention (parameterized queries)
- Access control (farmer-specific data)
- CSRF protection (Flask default)

### Security Best Practices
- Never commit `.env` file
- Use strong SECRET_KEY in production
- Enable HTTPS in production
- Regular security updates
- Implement rate limiting
- Monitor logs for suspicious activity

---

## 📈 Performance

### Optimization Tips
- Use connection pooling for database
- Cache weather API responses (5-10 minutes)
- Implement pagination for large lists
- Use indexes on frequently queried columns
- Compress static assets
- Enable gzip compression

### Database Optimization
```sql
-- Analyze tables
ANALYZE TABLE Farmers, Crops, SoilRecords, IrrigationHistory, IrrigationSchedule;

-- Optimize tables
OPTIMIZE TABLE Farmers, Crops, SoilRecords, IrrigationHistory, IrrigationSchedule;
```

---

## 🚀 Deployment

### Production Checklist
- [ ] Change SECRET_KEY to strong random value
- [ ] Set FLASK_ENV=production
- [ ] Use strong database password
- [ ] Enable HTTPS
- [ ] Disable debug mode
- [ ] Setup automated backups
- [ ] Configure monitoring
- [ ] Setup error logging
- [ ] Implement rate limiting
- [ ] Setup firewall rules

### Deployment Options

#### Option 1: Traditional Server (Ubuntu + Nginx + Gunicorn)
```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 127.0.0.1:8000 run:app

# Configure Nginx as reverse proxy
```

#### Option 2: Docker
```bash
# Build image
docker build -t smart-farming .

# Run container
docker run -p 8000:8000 smart-farming
```

#### Option 3: Cloud Platforms
- **Heroku**: `git push heroku main`
- **AWS Elastic Beanstalk**: `eb deploy`
- **Azure App Service**: `az webapp up`

For detailed deployment guides, see [COMPLETE_PROJECT_DOCUMENTATION.md](COMPLETE_PROJECT_DOCUMENTATION.md).

---

## 🔮 Roadmap

### Version 2.0 (Planned)
- [ ] Mobile application (Android/iOS)
- [ ] Advanced analytics dashboard
- [ ] IoT sensor integration
- [ ] Multi-language support (Telugu, Hindi, Tamil)
- [ ] Community features (forums, Q&A)
- [ ] Advanced ML models (LSTM, CNN)
- [ ] Government scheme integration
- [ ] Payment integration

### Version 1.1 (In Progress)
- [ ] Email notifications
- [ ] SMS alerts
- [ ] Export reports (PDF)
- [ ] Crop disease detection
- [ ] Yield prediction

---

## 📊 Project Statistics

- **Total Files**: 50+
- **Lines of Code**: ~5000+
- **Database Tables**: 5
- **API Endpoints**: 15+
- **ML Models**: 2
- **Supported Crops**: 22
- **Growth Stages**: 4 (FAO-56)
- **Documentation Pages**: 8+

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2026 Smart Farming Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🙏 Acknowledgments

- [OpenWeatherMap](https://openweathermap.org/) for weather API
- [scikit-learn](https://scikit-learn.org/) for ML framework
- [Flask](https://flask.palletsprojects.com/) for web framework
- [Bootstrap](https://getbootstrap.com/) for UI framework
- All contributors and testers

---

## 📞 Contact

### Project Maintainers
- **Name**: Your Name
- **Email**: your.email@example.com
- **GitHub**: [@yourusername](https://github.com/yourusername)

### Support
- **Issues**: [GitHub Issues](https://github.com/yourusername/smart-farming-irrigation/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/smart-farming-irrigation/discussions)
- **Email**: support@smartfarming.com

### Links
- **Website**: https://smartfarming.com
- **Documentation**: https://docs.smartfarming.com
- **Demo**: https://demo.smartfarming.com

---

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/smart-farming-irrigation&type=Date)](https://star-history.com/#yourusername/smart-farming-irrigation&Date)

---

## 📈 Activity

![GitHub commit activity](https://img.shields.io/github/commit-activity/m/yourusername/smart-farming-irrigation)
![GitHub last commit](https://img.shields.io/github/last-commit/yourusername/smart-farming-irrigation)
![GitHub issues](https://img.shields.io/github/issues/yourusername/smart-farming-irrigation)
![GitHub pull requests](https://img.shields.io/github/issues-pr/yourusername/smart-farming-irrigation)

---

<div align="center">

**Made with ❤️ for Farmers**

**Happy Farming! 🌾💧**

[⬆ Back to Top](#-smart-farming-irrigation-system)

</div>
