# Complete Project Documentation - Smart Farming Irrigation System

## Table of Contents
1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Technology Stack](#technology-stack)
4. [Database Design](#database-design)
5. [Application Structure](#application-structure)
6. [Core Features](#core-features)
7. [API Endpoints](#api-endpoints)
8. [Machine Learning Models](#machine-learning-models)
9. [Installation Guide](#installation-guide)
10. [Configuration](#configuration)
11. [Usage Guide](#usage-guide)
12. [Testing](#testing)
13. [Deployment](#deployment)
14. [Troubleshooting](#troubleshooting)
15. [Future Enhancements](#future-enhancements)

---

## Project Overview

### Purpose
Smart Farming Irrigation System is an AI-powered web application that helps farmers optimize water usage through intelligent irrigation recommendations based on:
- Real-time weather data
- Soil conditions
- Crop growth stages
- Machine learning predictions

### Key Benefits
- **Water Conservation**: Reduce water usage by 20-40%
- **Increased Yield**: Optimal irrigation timing improves crop health
- **Cost Savings**: Lower water and electricity costs
- **Data-Driven**: Scientific approach to irrigation management
- **Easy to Use**: Simple web interface accessible from any device

### Target Users
- Small to medium-scale farmers
- Agricultural cooperatives
- Farm managers
- Agricultural extension workers

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│  (HTML/CSS/JavaScript - Bootstrap 5 + Custom Styling)          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FLASK APPLICATION                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Routes     │  │   Services   │  │    Models    │         │
│  │  (Views)     │  │  (Business)  │  │    (Data)    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────┬────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│    MySQL     │  │  Weather API │  │  ML Models   │
│   Database   │  │ (OpenWeather)│  │  (Pickle)    │
└──────────────┘  └──────────────┘  └──────────────┘
```

### Component Breakdown

#### 1. Frontend Layer
- **Templates**: Jinja2 templates with Bootstrap 5
- **Static Assets**: CSS, JavaScript, images
- **Responsive Design**: Mobile-first approach
- **Interactive Features**: Live location, dynamic forms

#### 2. Application Layer (Flask)
- **Routes**: Handle HTTP requests and responses
- **Services**: Business logic and calculations
- **Models**: Database interaction layer
- **Middleware**: Authentication, error handling

#### 3. Data Layer
- **MySQL Database**: Persistent data storage
- **External APIs**: Weather data integration
- **ML Models**: Crop and soil predictions

---

## Technology Stack

### Backend
- **Framework**: Flask 2.3+
- **Language**: Python 3.8+
- **Database**: MySQL 8.0+
- **ORM**: PyMySQL (raw SQL with dict cursors)
- **Authentication**: Werkzeug security (PBKDF2)

### Frontend
- **Template Engine**: Jinja2
- **CSS Framework**: Bootstrap 5.3
- **Icons**: Bootstrap Icons
- **JavaScript**: Vanilla JS + Geolocation API

### External Services
- **Weather API**: OpenWeatherMap API
- **Geocoding**: OpenWeatherMap Geocoding API

### Machine Learning
- **Framework**: scikit-learn
- **Models**: 
  - Random Forest (Crop Recommendation)
  - Random Forest (Soil Fertility)
- **Storage**: Pickle files

### Development Tools
- **Version Control**: Git
- **Package Manager**: pip
- **Virtual Environment**: venv
- **Code Editor**: Any (VS Code recommended)

---

## Database Design

### Complete Schema

See [DATABASE_ERD.md](DATABASE_ERD.md) for detailed Entity Relationship Diagram.

### Tables Summary

| Table | Purpose | Records/Year (per farmer) |
|-------|---------|---------------------------|
| Farmers | User accounts | 1 |
| Crops | Crop information | 2-5 |
| SoilRecords | Soil test results | 10-20 |
| IrrigationHistory | Past irrigation events | 50-100 |
| IrrigationSchedule | Future irrigation plan | 200-600 |

### Key Relationships
- 1 Farmer → Many Crops
- 1 Crop → Many Irrigation Records
- 1 Crop → Many Soil Records
- 1 Crop → Many Schedule Entries

---

## Application Structure

### Directory Layout

```
ecofriendly_anti/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── config.py                # Configuration settings
│   ├── database.py              # Database connection
│   ├── models/                  # Data models
│   │   ├── __init__.py
│   │   ├── farmer.py            # Farmer CRUD
│   │   ├── crop.py              # Crop CRUD
│   │   ├── soil.py              # Soil CRUD
│   │   ├── irrigation.py        # Irrigation history CRUD
│   │   └── schedule.py          # Schedule CRUD
│   ├── routes/                  # Route handlers
│   │   ├── __init__.py
│   │   ├── auth.py              # Login/Register
│   │   ├── main.py              # Dashboard
│   │   ├── crops.py             # Crop management
│   │   └── irrigation.py        # Irrigation features
│   └── services/                # Business logic
│       ├── __init__.py
│       ├── weather.py           # Weather API integration
│       ├── ml_engine.py         # ML predictions
│       ├── irrigation_engine.py # Irrigation calculations
│       ├── scheduler.py         # Basic scheduling
│       └── advanced_scheduler.py# Full lifecycle scheduling
├── templates/                   # HTML templates
│   ├── base.html               # Base layout
│   ├── index.html              # Landing page
│   ├── auth/                   # Authentication pages
│   ├── main/                   # Dashboard pages
│   ├── crops/                  # Crop pages
│   └── irrigation/             # Irrigation pages
├── static/                     # Static assets
│   ├── css/                    # Stylesheets
│   ├── js/                     # JavaScript files
│   └── images/                 # Images (if any)
├── models/                     # ML model files
│   ├── crop_model.pkl
│   ├── crop_label_encoder.pkl
│   ├── crop_accuracy.pkl
│   ├── soil_model.pkl
│   └── soil_accuracy.pkl
├── data/                       # Data files
│   ├── farming.db              # SQLite (legacy)
│   ├── crop_recommendation_dataset_final.csv
│   ├── soil_fertility_dataset.csv
│   ├── irrigation_history.csv
│   └── weather_history.csv
├── src/                        # Training scripts
│   ├── crop_train.py           # Train crop model
│   ├── soil_train.py           # Train soil model
│   ├── predict.py              # Prediction utilities
│   └── weather_api.py          # Weather utilities
├── .env                        # Environment variables
├── requirements.txt            # Python dependencies
├── run.py                      # Application entry point
└── init_db.py                  # Database initialization
```

### Module Responsibilities

#### Models Layer (`app/models/`)
- **Purpose**: Database interaction
- **Pattern**: Repository pattern
- **Functions**: CRUD operations
- **No Business Logic**: Pure data access

#### Routes Layer (`app/routes/`)
- **Purpose**: HTTP request handling
- **Pattern**: Blueprint-based routing
- **Responsibilities**: 
  - Request validation
  - Response rendering
  - Session management
  - Flash messages

#### Services Layer (`app/services/`)
- **Purpose**: Business logic
- **Pattern**: Service layer pattern
- **Responsibilities**:
  - Calculations
  - External API calls
  - ML predictions
  - Complex workflows

---

## Core Features

### 1. User Authentication
**Files**: `app/routes/auth.py`, `app/models/farmer.py`

**Features**:
- User registration with validation
- Secure login (password hashing)
- Session management
- Login required decorator
- Last login tracking

**Security**:
- PBKDF2-SHA256 password hashing
- Session-based authentication
- CSRF protection (Flask default)

### 2. Crop Management
**Files**: `app/routes/crops.py`, `app/models/crop.py`

**Features**:
- Add new crops with planting date
- View all crops (active/harvested)
- Crop recommendation using ML
- Soil fertility prediction
- Crop status tracking

**ML Integration**:
- Random Forest classifier
- Input: N, P, K, pH, rainfall, temperature
- Output: Recommended crop with confidence

### 3. Irrigation Recommendation
**Files**: `app/routes/irrigation.py`, `app/services/irrigation_engine.py`

**Features**:
- Real-time weather integration
- Growth stage detection (4 FAO-56 stages)
- ET₀ calculation (Penman-Monteith simplified)
- Soil moisture consideration
- Irrigation decision logic

**Calculation Flow**:
```
Weather Data + Soil Moisture + Growth Stage
    ↓
ET₀ = 0.5 × Temperature
    ↓
ETc = ET₀ × Kc (crop coefficient)
    ↓
Net Water = ETc - Rainfall
    ↓
Decision Logic (based on soil moisture + net water)
```

### 4. Full Lifecycle Scheduling
**Files**: `app/services/advanced_scheduler.py`

**Features**:
- Generate complete irrigation schedule (planting to harvest)
- Daily moisture simulation
- Rainfall impact consideration
- Missed irrigation detection
- Schedule recalculation
- Status tracking (pending/completed/missed/skipped)

**Schedule Generation**:
```python
for day in range(growth_duration):
    date = planting_date + timedelta(days=day)
    stage = determine_stage(day)
    etc = calculate_etc(stage.kc, weather)
    moisture -= etc
    moisture += rainfall
    if moisture < threshold:
        schedule_irrigation(date, water_needed)
        moisture += water_needed
```

### 5. Weather Integration
**Files**: `app/services/weather.py`

**Features**:
- Current weather by city name
- Current weather by GPS coordinates
- 5-day forecast
- District name mapping (Telangana)
- Fuzzy matching for spelling errors

**API Endpoints Used**:
- Current Weather: `api.openweathermap.org/data/2.5/weather`
- Forecast: `api.openweathermap.org/data/2.5/forecast`
- Geocoding: `api.openweathermap.org/geo/1.0/direct`

### 6. Dashboard & Analytics
**Files**: `app/routes/main.py`, `templates/main/dashboard.html`

**Features**:
- Active crops overview
- Recent irrigation history
- Upcoming schedule
- Water savings metrics
- Quick action buttons

---

## API Endpoints

### Authentication Routes (`/auth`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/auth/register` | Registration form | No |
| POST | `/auth/register` | Create new account | No |
| GET | `/auth/login` | Login form | No |
| POST | `/auth/login` | Authenticate user | No |
| GET | `/auth/logout` | End session | Yes |

### Main Routes (`/`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | Landing page | No |
| GET | `/dashboard` | Main dashboard | Yes |

### Crop Routes (`/crops`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/crops/recommend` | Crop recommendation form | Yes |
| POST | `/crops/recommend` | Get crop recommendation | Yes |
| POST | `/crops/confirm` | Save recommended crop | Yes |
| GET | `/crops/my-crops` | View all crops | Yes |

### Irrigation Routes (`/irrigation`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/irrigation/` | Irrigation dashboard | Yes |
| GET | `/irrigation/<crop_id>` | Today's advice | Yes |
| POST | `/irrigation/<crop_id>` | Calculate irrigation | Yes |
| GET | `/irrigation/<crop_id>/weekly` | 5-day forecast plan | Yes |
| GET | `/irrigation/history` | Irrigation history | Yes |
| GET | `/irrigation/<crop_id>/schedule` | Full lifecycle schedule | Yes |
| POST | `/irrigation/<crop_id>/schedule/generate` | Generate/regenerate schedule | Yes |
| POST | `/irrigation/<crop_id>/schedule/recalculate` | Recalculate after missed | Yes |
| POST | `/irrigation/schedule/<id>/complete` | Mark irrigation done | Yes |
| POST | `/irrigation/weather/live` | Get weather by GPS | Yes |

---

## Machine Learning Models

### 1. Crop Recommendation Model

**File**: `models/crop_model.pkl`  
**Training Script**: `src/crop_train.py`  
**Algorithm**: Random Forest Classifier

**Input Features** (7):
- N (Nitrogen): 0-140 kg/ha
- P (Phosphorus): 5-145 kg/ha
- K (Potassium): 5-205 kg/ha
- pH: 3.5-9.9
- Rainfall: 20-300 mm
- Temperature: 8-43°C
- Humidity: 14-100%

**Output**:
- Crop name (22 classes)
- Confidence score

**Supported Crops**:
rice, maize, chickpea, kidneybeans, pigeonpeas, mothbeans, mungbean, blackgram, lentil, pomegranate, banana, mango, grapes, watermelon, muskmelon, apple, orange, papaya, coconut, cotton, jute, coffee

**Accuracy**: ~99% (on training data)

### 2. Soil Fertility Model

**File**: `models/soil_model.pkl`  
**Training Script**: `src/soil_train.py`  
**Algorithm**: Random Forest Classifier

**Input Features** (7):
- N (Nitrogen)
- P (Phosphorus)
- K (Potassium)
- pH
- Sand percentage
- Clay percentage
- Moisture percentage

**Output**:
- Fertility class: Low, Medium, High

**Usage**: Helps farmers understand soil health

---

## Installation Guide

### Prerequisites

1. **Python 3.8+**
```bash
python --version
```

2. **MySQL 8.0+**
```bash
mysql --version
```

3. **Git** (optional)
```bash
git --version
```

### Step-by-Step Installation

#### 1. Clone or Download Project
```bash
git clone <repository-url>
cd ecofriendly_anti
```

#### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Setup MySQL Database

Follow [MYSQL_SETUP.md](MYSQL_SETUP.md) to:
- Create database `smart_farming`
- Create user `farming_user`
- Create all tables
- Grant permissions

#### 5. Configure Environment Variables

Create `.env` file:
```env
# Flask Configuration
SECRET_KEY=your-secret-key-here-change-this
FLASK_ENV=development

# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_NAME=smart_farming
DB_USER=farming_user
DB_PASSWORD=farming_secure_password_2024

# Weather API Configuration
OPENWEATHER_API_KEY=your-api-key-here
```

#### 6. Get OpenWeather API Key

1. Visit: https://openweathermap.org/api
2. Sign up for free account
3. Get API key from dashboard
4. Add to `.env` file

#### 7. Run Application
```bash
python run.py
```

#### 8. Access Application
Open browser: http://localhost:5000

---

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| SECRET_KEY | Flask session encryption | - | Yes |
| FLASK_ENV | Environment mode | production | No |
| DB_HOST | MySQL host | localhost | Yes |
| DB_PORT | MySQL port | 3306 | Yes |
| DB_NAME | Database name | smart_farming | Yes |
| DB_USER | Database user | farming_user | Yes |
| DB_PASSWORD | Database password | - | Yes |
| OPENWEATHER_API_KEY | Weather API key | - | Yes |

### Application Configuration

**File**: `app/config.py`

```python
class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 3306))
    DB_NAME = os.getenv("DB_NAME", "smart_farming")
    DB_USER = os.getenv("DB_USER", "farming_user")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
```

---

## Usage Guide

### For Farmers

#### 1. Register Account
1. Go to `/auth/register`
2. Enter username, password, full name, location
3. Click "Register"

#### 2. Add First Crop
1. Login to dashboard
2. Click "Get Crop Recommendation"
3. Enter soil test results (N, P, K, pH, moisture, sand, clay)
4. Get ML-based crop recommendation
5. Confirm and add crop with planting date

#### 3. Get Irrigation Advice
1. Go to "Irrigation" from dashboard
2. Select your crop
3. Enter current soil moisture
4. Click "Calculate & Save"
5. View recommendation (irrigate/skip)

#### 4. View Full Schedule
1. From irrigation page, click "View Full Schedule"
2. See complete irrigation plan (planting to harvest)
3. Mark irrigations as completed
4. Regenerate if needed with new soil moisture

#### 5. Track History
1. Go to "Irrigation History"
2. View all past irrigation events
3. See water savings

### For Developers

#### Adding New Routes
```python
# app/routes/new_feature.py
from flask import Blueprint

new_bp = Blueprint("new_feature", __name__, url_prefix="/new")

@new_bp.route("/")
def index():
    return render_template("new_feature/index.html")

# Register in app/__init__.py
from app.routes.new_feature import new_bp
app.register_blueprint(new_bp)
```

#### Adding New Models
```python
# app/models/new_model.py
from app.database import query_db, execute_db

def create_record(data):
    return execute_db(
        "INSERT INTO TableName (col1, col2) VALUES (%s, %s)",
        (data["col1"], data["col2"])
    )

def get_records():
    return query_db("SELECT * FROM TableName")
```

#### Adding New Services
```python
# app/services/new_service.py
def calculate_something(input_data):
    # Business logic here
    result = input_data * 2
    return result
```

---

## Testing

### Manual Testing Checklist

#### Authentication
- [ ] Register new user
- [ ] Login with correct credentials
- [ ] Login with wrong credentials (should fail)
- [ ] Logout
- [ ] Access protected route without login (should redirect)

#### Crop Management
- [ ] Add crop with recommendation
- [ ] View all crops
- [ ] Add multiple crops
- [ ] Check crop status updates

#### Irrigation
- [ ] Get today's advice
- [ ] Calculate with different soil moisture values
- [ ] View 5-day forecast
- [ ] Generate full schedule
- [ ] Mark irrigation as completed
- [ ] Detect missed irrigations
- [ ] Recalculate schedule

#### Weather Integration
- [ ] Get weather by city name
- [ ] Get weather by GPS coordinates
- [ ] Handle invalid city names
- [ ] Handle API errors

### Unit Testing (Future)

```python
# tests/test_irrigation_engine.py
import unittest
from app.services.irrigation_engine import calculate_irrigation

class TestIrrigationEngine(unittest.TestCase):
    def test_calculate_irrigation(self):
        result = calculate_irrigation(
            temperature=30,
            rainfall=0,
            kc=1.15,
            soil_moisture=40
        )
        self.assertIn("et0", result)
        self.assertIn("decision", result)
```

---

## Deployment

### Production Checklist

#### 1. Security
- [ ] Change SECRET_KEY to strong random value
- [ ] Set FLASK_ENV=production
- [ ] Use strong database password
- [ ] Enable HTTPS
- [ ] Set secure session cookies
- [ ] Implement rate limiting

#### 2. Database
- [ ] Setup automated backups
- [ ] Configure connection pooling
- [ ] Optimize indexes
- [ ] Setup monitoring

#### 3. Application
- [ ] Use production WSGI server (Gunicorn)
- [ ] Setup reverse proxy (Nginx)
- [ ] Configure logging
- [ ] Setup error monitoring (Sentry)

### Deployment Options

#### Option 1: Traditional Server (Ubuntu)

```bash
# Install dependencies
sudo apt update
sudo apt install python3-pip python3-venv nginx mysql-server

# Setup application
cd /var/www/smart-farming
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 127.0.0.1:8000 run:app

# Configure Nginx
sudo nano /etc/nginx/sites-available/smart-farming
```

Nginx configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /var/www/smart-farming/static;
    }
}
```

#### Option 2: Docker

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "run:app"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DB_HOST=db
    depends_on:
      - db

  db:
    image: mysql:8.0
    environment:
      MYSQL_DATABASE: smart_farming
      MYSQL_USER: farming_user
      MYSQL_PASSWORD: secure_password
      MYSQL_ROOT_PASSWORD: root_password
    volumes:
      - mysql_data:/var/lib/mysql

volumes:
  mysql_data:
```

#### Option 3: Cloud Platforms

**Heroku**:
```bash
# Install Heroku CLI
heroku login
heroku create smart-farming-app
heroku addons:create cleardb:ignite
git push heroku main
```

**AWS Elastic Beanstalk**:
```bash
eb init -p python-3.9 smart-farming
eb create smart-farming-env
eb deploy
```

---

## Troubleshooting

### Common Issues

#### 1. Database Connection Error
```
Error: Can't connect to MySQL server
```

**Solutions**:
- Check MySQL is running: `sudo systemctl status mysql`
- Verify credentials in `.env`
- Check firewall: `sudo ufw allow 3306`
- Test connection: `mysql -u farming_user -p`

#### 2. Weather API Error
```
Error: Weather data not available
```

**Solutions**:
- Check API key is valid
- Verify API key in `.env`
- Check API quota (free tier: 60 calls/minute)
- Try different city name
- Check internet connection

#### 3. Import Error
```
ModuleNotFoundError: No module named 'flask'
```

**Solutions**:
- Activate virtual environment
- Install dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version`

#### 4. Template Not Found
```
TemplateNotFound: irrigation/advice.html
```

**Solutions**:
- Check file exists in `templates/irrigation/`
- Check file name spelling
- Restart Flask application

#### 5. Session Error
```
RuntimeError: The session is unavailable
```

**Solutions**:
- Set SECRET_KEY in `.env`
- Check `.env` is loaded
- Restart application

### Debug Mode

Enable debug mode for development:

```python
# run.py
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
```

**Warning**: Never use debug=True in production!

### Logging

Add logging for troubleshooting:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")
```

---

## Future Enhancements

### Planned Features

#### 1. Mobile Application
- Native Android/iOS apps
- Push notifications for irrigation reminders
- Offline mode support

#### 2. Advanced Analytics
- Water usage trends
- Yield prediction
- Cost-benefit analysis
- Comparative analysis with neighbors

#### 3. IoT Integration
- Soil moisture sensors
- Automated irrigation valves
- Weather stations
- Real-time monitoring dashboard

#### 4. Multi-Language Support
- Telugu, Hindi, Tamil, Kannada
- Language selection in settings
- Localized content

#### 5. Community Features
- Farmer forums
- Expert Q&A
- Success stories
- Best practices sharing

#### 6. Advanced ML Models
- LSTM for rainfall prediction
- CNN for crop disease detection
- Yield prediction models
- Price forecasting

#### 7. Government Integration
- Subsidy information
- Scheme eligibility checker
- Market price integration
- Weather alerts

#### 8. Payment Integration
- Premium features
- Subscription plans
- Expert consultation booking

### Technical Improvements

#### 1. Performance
- Redis caching
- Database query optimization
- CDN for static assets
- Lazy loading

#### 2. Security
- Two-factor authentication
- API rate limiting
- Input sanitization
- Security headers

#### 3. Testing
- Unit tests (pytest)
- Integration tests
- End-to-end tests (Selenium)
- Load testing (Locust)

#### 4. DevOps
- CI/CD pipeline (GitHub Actions)
- Automated deployments
- Monitoring (Prometheus + Grafana)
- Log aggregation (ELK stack)

---

## Contributing

### How to Contribute

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -m "Add new feature"`
4. Push to branch: `git push origin feature/new-feature`
5. Create Pull Request

### Code Style

- Follow PEP 8 for Python
- Use meaningful variable names
- Add docstrings to functions
- Comment complex logic
- Keep functions small and focused

### Commit Messages

```
feat: Add new irrigation algorithm
fix: Resolve weather API timeout issue
docs: Update installation guide
refactor: Simplify schedule generation
test: Add unit tests for irrigation engine
```

---

## License

This project is licensed under the MIT License.

---

## Support

### Documentation
- [Database ERD](DATABASE_ERD.md)
- [MySQL Setup](MYSQL_SETUP.md)
- [Quick Start](QUICK_START_IRRIGATION.md)
- [UI State Sync Fix](UI_STATE_SYNC_FIX.md)

### Contact
- Email: support@smartfarming.com
- GitHub Issues: [Create Issue]
- Forum: [Community Forum]

---

## Acknowledgments

- OpenWeatherMap for weather API
- scikit-learn for ML framework
- Flask community for excellent documentation
- Bootstrap team for UI framework
- All contributors and testers

---

**Version**: 1.0.0  
**Last Updated**: February 22, 2026  
**Status**: Production Ready ✅

