import os
import csv
import joblib
from datetime import datetime
from weather_api import select_location, get_weather

print("\n🌾 FULL SMART STAGE-BASED IRRIGATION SYSTEM")
print("--------------------------------------------------")

# ---------------------------------------------------
# Load Crop Model to Get All Crop Names
# ---------------------------------------------------

try:
    crop_label_encoder = joblib.load("models/crop_label_encoder.pkl")
    ALL_CROPS = list(crop_label_encoder.classes_)
except:
    print("⚠ Could not load crop model. Using default crops.")
    ALL_CROPS = ["rice", "wheat", "maize"]

# ---------------------------------------------------
# Crop Duration (Average Realistic Days)
# You can modify based on Telangana crops
# ---------------------------------------------------

CROP_DURATION = {
    "rice": 120,
    "wheat": 110,
    "maize": 100,
    "cotton": 160,
    "potato": 90,
    "sugarcane": 300,
    "soybean": 100,
    "groundnut": 110,
    "chickpea": 100,
    "mango": 365
}

# Default duration if crop not found
DEFAULT_DURATION = 100

# ---------------------------------------------------
# Function to Generate Stage Data Automatically
# ---------------------------------------------------

def generate_crop_stages(total_days):
    return {
        "initial": {
            "duration": int(total_days * 0.2),
            "kc": 0.7
        },
        "development": {
            "duration": int(total_days * 0.3),
            "kc": 0.95
        },
        "mid": {
            "duration": int(total_days * 0.3),
            "kc": 1.15
        },
        "late": {
            "duration": int(total_days * 0.2),
            "kc": 0.8
        }
    }

# ---------------------------------------------------
# User Input
# ---------------------------------------------------

city = select_location()
weather = get_weather(city)

print("\nAvailable Crops:")
for c in ALL_CROPS:
    print("-", c)

crop = input("\nEnter Crop Name: ").lower()

if crop not in ALL_CROPS:
    print("⚠ Crop not in trained dataset. Using default settings.")

total_days = CROP_DURATION.get(crop, DEFAULT_DURATION)
stages = generate_crop_stages(total_days)

planting_date_str = input("Enter Planting Date (YYYY-MM-DD): ")
soil_moisture = float(input("Enter Soil Moisture (%): "))

planting_date = datetime.strptime(planting_date_str, "%Y-%m-%d")
today = datetime.now()

days_after_sowing = (today - planting_date).days

# ---------------------------------------------------
# Determine Growth Stage Automatically
# ---------------------------------------------------

stage = "late"
kc = 1.0
cumulative_days = 0

for stage_name, stage_data in stages.items():
    cumulative_days += stage_data["duration"]
    if days_after_sowing <= cumulative_days:
        stage = stage_name
        kc = stage_data["kc"]
        break

# If crop exceeded duration
if days_after_sowing > total_days:
    stage = "harvest-ready"
    kc = 0.6

# ---------------------------------------------------
# Irrigation Calculation
# ---------------------------------------------------

temperature = weather["temp"]
rainfall = weather["rain"]

# Simplified ET₀ Formula
ET0 = 0.5 * temperature

crop_water = ET0 * kc
net_water = crop_water - rainfall
net_water = max(net_water, 0)

# Soil Moisture Adjustment
if soil_moisture > 70:
    net_water = 0
    decision = "No irrigation needed (Soil already wet)"
elif soil_moisture < 35:
    decision = "Full irrigation required"
else:
    decision = "Moderate irrigation"

# ---------------------------------------------------
# Output
# ---------------------------------------------------

print("\n📍 Location:", city)
print("🌡 Temperature:", temperature, "°C")
print("🌧 Rainfall:", rainfall, "mm")

print("\n🌱 Crop Details")
print("Total Growing Days:", total_days)
print("Days After Sowing:", days_after_sowing)
print("Current Stage:", stage)
print("Kc Used:", kc)

print("\n💧 Irrigation Recommendation")
print("ET₀:", round(ET0, 2))
print("Water Required:", round(net_water, 2), "liters/plant")
print("Decision:", decision)

# ---------------------------------------------------
# Save History
# ---------------------------------------------------

os.makedirs("data", exist_ok=True)
file_path = "data/irrigation_history.csv"
file_exists = os.path.isfile(file_path)

with open(file_path, "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    if not file_exists:
        writer.writerow([
            "date","city","crop","stage",
            "days_after_sowing","water_required","decision"
        ])
    writer.writerow([
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        city,
        crop,
        stage,
        days_after_sowing,
        round(net_water,2),
        decision
    ])

print("\n✅ Irrigation record saved successfully!")