import pandas as pd
import joblib
import os
from weather_api import get_weather
from weather_api import select_location
# ---------------------------------------------------
# Load Models From Main models/ Folder
# ---------------------------------------------------

MODEL_DIR = "models"   # models folder outside src

try:
    soil_model = joblib.load(os.path.join(MODEL_DIR, "soil_model.pkl"))
    soil_accuracy = joblib.load(os.path.join(MODEL_DIR, "soil_accuracy.pkl"))

    crop_model = joblib.load(os.path.join(MODEL_DIR, "crop_model.pkl"))
    crop_label_encoder = joblib.load(os.path.join(MODEL_DIR, "crop_label_encoder.pkl"))
    crop_accuracy = joblib.load(os.path.join(MODEL_DIR, "crop_accuracy.pkl"))

except Exception as e:
    print("❌ Error loading model files.")
    print("Make sure models folder is in main project directory.")
    print("Expected structure:")
    print("ecofriendly/")
    print("   ├── models/")
    print("   └── src/")
    print("Error:", e)
    exit()

# ---------------------------------------------------
# Helper Functions
# ---------------------------------------------------

def detect_season(month):
    if month in [6, 7, 8, 9]:
        return "Monsoon"
    elif month in [10, 11, 12, 1]:
        return "Winter"
    else:
        return "Summer"


def soil_nature_from_texture(sand, clay):
    if sand > 60:
        return "Sandy"
    elif clay > 40:
        return "Clayey"
    else:
        return "Loamy"


# ---------------------------------------------------
# Display Model Accuracy
# ---------------------------------------------------

print("\n📊 Model Evaluation")
print("------------------------")
print(f"Soil Fertility Accuracy : {soil_accuracy * 100:.2f}%")
print(f"Crop Recommendation Accuracy : {crop_accuracy * 100:.2f}%")

# ---------------------------------------------------
# User Input
# ---------------------------------------------------

print("\n🌱 Enter Soil Details")
print("-----------------------")

try:
    N = float(input("Nitrogen (N): "))
    P = float(input("Phosphorus (P): "))
    K = float(input("Potassium (K): "))
    ph = float(input("pH Value: "))
    moisture = float(input("Moisture (%): "))
    sand = float(input("Sand (%): "))
    clay = float(input("Clay (%): "))
    city = select_location()
    month = int(input("Current Month (1-12): "))

except ValueError:
    print("❌ Invalid input. Please enter correct numeric values.")
    exit()

# ---------------------------------------------------
# Get Weather Data
# ---------------------------------------------------

try:
    weather = get_weather(city)

    temperature = weather["temp"]
    humidity = weather["humidity"]
    rainfall = weather["rain"]

except Exception as e:
    print("❌ Weather API Error.")
    print("Check city name or API key in weather_api.py")
    print("Error:", e)
    exit()

# ---------------------------------------------------
# Soil Prediction
# ---------------------------------------------------

soil_features = pd.DataFrame(
    [[N, P, K, ph, moisture]],
    columns=['N', 'P', 'K', 'ph', 'moisture']
)

soil_fertility = soil_model.predict(soil_features)[0]
soil_nature = soil_nature_from_texture(sand, clay)

# ---------------------------------------------------
# Season Detection
# ---------------------------------------------------

season = detect_season(month)

# ---------------------------------------------------
# Crop Prediction
# ---------------------------------------------------

crop_features = pd.DataFrame(
    [[N, P, K, ph, temperature, humidity, rainfall]],
    columns=['N', 'P', 'K', 'ph', 'temperature', 'humidity', 'rainfall']
)

crop_encoded = crop_model.predict(crop_features)[0]
recommended_crop = crop_label_encoder.inverse_transform([crop_encoded])[0]

# ---------------------------------------------------
# Crop Duration
# ---------------------------------------------------

crop_duration = {
    "Rice": "120 days",
    "Wheat": "110 days",
    "Maize": "100 days",
    "Cotton": "160 days",
    "Potato": "90 days"
}

growing_time = crop_duration.get(recommended_crop, "Varies")

# ---------------------------------------------------
# Final Output
# ---------------------------------------------------

print("\n🌍 Weather Report")
print("---------------------")
print(f"Temperature : {temperature} °C")
print(f"Humidity    : {humidity} %")
print(f"Rainfall    : {rainfall} mm")

print("\n🌱 Soil Health Report")
print("---------------------")
print(f"Soil Nature    : {soil_nature}")
print(f"Soil Fertility : {soil_fertility}")

print("\n📅 Current Farming Season")
print("--------------------------")
print(f"Season : {season}")

print("\n🌾 Crop Recommendation")
print("-----------------------")
print(f"Recommended Crop  : {recommended_crop}")
print(f"Growing Time      : {growing_time}")

print("\n✅ Final Advice")
print("This crop is suitable for your soil and season.")
print("You can safely proceed with cultivation.")
