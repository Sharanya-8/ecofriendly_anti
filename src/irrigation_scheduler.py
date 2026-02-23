from weather_api import get_weather_forecast
from weather_api import select_location
# Crop water needs (liters/day)
CROP_WATER_NEEDS = {
    "rice": 6,
    "wheat": 4,
    "maize": 5,
    "cotton": 5,
    "potato": 4,
    "mango": 2
}

print("\n🌱 7-DAY SMART IRRIGATION SCHEDULER")
print("----------------------------------")

city = select_location()
crop = input("Enter crop: ").lower()
soil_moisture = float(input("Soil moisture (%): "))

base_water = CROP_WATER_NEEDS.get(crop, 4)

try:
    forecast = get_weather_forecast(city)
except Exception as e:
    print("❌ Weather forecast error:", e)
    exit()

total_saved = 0

print("\n📅 WEEKLY IRRIGATION PLAN\n")

for day in forecast:
    date = day["date"]
    rain = day["rain"]
    temp = day["temp"]
    humidity = day["humidity"]

    if rain > 5:
        decision = "Rain expected 🌧 — Skip irrigation"
        water = 0
        saved = base_water

    elif soil_moisture > 70:
        decision = "Soil wet — No irrigation"
        water = 0
        saved = base_water

    elif temp > 34:
        decision = "Hot day — Full irrigation"
        water = base_water * 1.2
        saved = 0

    else:
        decision = "Normal irrigation"
        water = base_water
        saved = 0

    total_saved += saved

    print(f"{date}")
    print(f" Temp: {temp}°C | Humidity: {humidity}% | Rain: {rain}mm")
    print(" Decision:", decision)
    print(" Water:", round(water, 2), "liters\n")

print("💧 TOTAL WATER SAVED THIS WEEK:", round(total_saved, 2), "liters")
