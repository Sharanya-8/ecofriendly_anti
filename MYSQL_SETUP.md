# MySQL Database Setup Guide

## Step 1: Install MySQL

### Windows:
1. Download MySQL Installer from: https://dev.mysql.com/downloads/installer/
2. Run the installer and select "Developer Default"
3. Set root password during installation
4. Complete the installation

### Verify Installation:
```bash
mysql --version
```

## Step 2: Create Database and User

Open MySQL Command Line Client or use:
```bash
mysql -u root -p
```

Then execute these commands one by one:

```sql
-- Create the database
CREATE DATABASE smart_farming CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create a dedicated user for the application
CREATE USER 'farming_user'@'localhost' IDENTIFIED BY 'farming_secure_password_2024';

-- Grant all privileges on the database to the user
GRANT ALL PRIVILEGES ON smart_farming.* TO 'farming_user'@'localhost';

-- Apply the changes
FLUSH PRIVILEGES;

-- Switch to the database
USE smart_farming;

-- Verify you're in the correct database
SELECT DATABASE();
```

## Step 3: Create Tables

Copy and paste each table creation command:

```sql
-- Table 1: Farmers (User accounts)
CREATE TABLE Farmers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(200) NOT NULL,
    location VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(150),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    INDEX idx_username (username)
) ENGINE=InnoDB;

-- Table 2: Crops (Multiple crops per farmer)
CREATE TABLE Crops (
    id INT AUTO_INCREMENT PRIMARY KEY,
    farmer_id INT NOT NULL,
    crop_name VARCHAR(100) NOT NULL,
    field_name VARCHAR(150) NOT NULL,
    planting_date DATE NOT NULL,
    growth_duration INT NOT NULL,
    status ENUM('active', 'harvested', 'failed') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (farmer_id) REFERENCES Farmers(id) ON DELETE CASCADE,
    INDEX idx_farmer_status (farmer_id, status),
    INDEX idx_planting_date (planting_date)
) ENGINE=InnoDB;

-- Table 3: SoilRecords (Soil test history)
CREATE TABLE SoilRecords (
    id INT AUTO_INCREMENT PRIMARY KEY,
    farmer_id INT NOT NULL,
    crop_id INT,
    N DECIMAL(8,2) NOT NULL,
    P DECIMAL(8,2) NOT NULL,
    K DECIMAL(8,2) NOT NULL,
    ph DECIMAL(4,2) NOT NULL,
    moisture DECIMAL(5,2) NOT NULL,
    sand DECIMAL(5,2),
    clay DECIMAL(5,2),
    soil_fertility VARCHAR(50),
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (farmer_id) REFERENCES Farmers(id) ON DELETE CASCADE,
    FOREIGN KEY (crop_id) REFERENCES Crops(id) ON DELETE SET NULL,
    INDEX idx_farmer_date (farmer_id, recorded_at),
    INDEX idx_crop (crop_id)
) ENGINE=InnoDB;

-- Table 4: IrrigationHistory (Past irrigation events)
CREATE TABLE IrrigationHistory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    farmer_id INT NOT NULL,
    crop_id INT NOT NULL,
    city VARCHAR(100),
    stage VARCHAR(50),
    days_after_sowing INT,
    et0 DECIMAL(8,3),
    kc DECIMAL(5,3),
    water_required DECIMAL(10,3),
    decision TEXT,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (farmer_id) REFERENCES Farmers(id) ON DELETE CASCADE,
    FOREIGN KEY (crop_id) REFERENCES Crops(id) ON DELETE CASCADE,
    INDEX idx_farmer_date (farmer_id, recorded_at),
    INDEX idx_crop_date (crop_id, recorded_at)
) ENGINE=InnoDB;

-- Table 5: IrrigationSchedule (30-day future schedule)
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

## Step 4: Verify Tables Created

```sql
-- Show all tables
SHOW TABLES;

-- Describe each table structure
DESCRIBE Farmers;
DESCRIBE Crops;
DESCRIBE SoilRecords;
DESCRIBE IrrigationHistory;
DESCRIBE IrrigationSchedule;
```

## Step 5: Insert Sample Data (Optional for Testing)

```sql
-- Sample farmer
INSERT INTO Farmers (username, password_hash, full_name, location, phone, email) 
VALUES ('demo_farmer', 'pbkdf2:sha256:600000$sample$hash', 'Demo Farmer', 'Hyderabad', '9876543210', 'demo@farm.com');

-- Check the data
SELECT * FROM Farmers;
```

## Step 6: Exit MySQL

```sql
EXIT;
```

## Connection Details for Application

Save these credentials (you'll need them in `.env` file):

```
DB_HOST=localhost
DB_PORT=3306
DB_NAME=smart_farming
DB_USER=farming_user
DB_PASSWORD=farming_secure_password_2024
```

## Troubleshooting

### If you get "Access Denied":
```sql
-- Login as root and recreate user
DROP USER 'farming_user'@'localhost';
CREATE USER 'farming_user'@'localhost' IDENTIFIED BY 'farming_secure_password_2024';
GRANT ALL PRIVILEGES ON smart_farming.* TO 'farming_user'@'localhost';
FLUSH PRIVILEGES;
```

### If you need to reset the database:
```sql
DROP DATABASE smart_farming;
-- Then repeat Step 2 and Step 3
```

### Check MySQL service status:
```bash
# Windows
net start MySQL80

# Or check services.msc
```

## Next Steps

After completing MySQL setup:
1. Update your `.env` file with database credentials
2. Install Python MySQL connector: `pip install pymysql cryptography`
3. Run the Flask application: `python run.py`
4. The application will automatically connect to MySQL
