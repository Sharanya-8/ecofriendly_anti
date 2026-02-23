import requests

API_KEY = "565cec5804b4568a5ff6bebbfdb68ad5"

DISTRICTS = [
    "Adilabad","Bhadradri Kothagudem","Hanumakonda","Hyderabad",
    "Jagtial","Jangaon","Jayashankar Bhupalpally","Jogulamba Gadwal",
    "Kamareddy","Karimnagar","Khammam","Komaram Bheem Asifabad",
    "Mahabubabad","Mahabubnagar","Mancherial","Medak",
    "Medchal-Malkajgiri","Mulugu","Nagarkurnool","Nalgonda",
    "Narayanpet","Nirmal","Nizamabad","Peddapalli",
    "Rajanna Sircilla","Rangareddy","Sangareddy",
    "Siddipet","Suryapet","Vikarabad","Wanaparthy",
    "Warangal","Yadadri Bhuvanagiri"
]

DISTRICTS.sort()


def search_district():
    while True:
        text = input("\nType district starting letters: ").lower()
        matches = [d for d in DISTRICTS if d.lower().startswith(text)]

        if not matches:
            print("❌ No match found.")
            continue

        for i, d in enumerate(matches, 1):
            print(f"{i}. {d}")

        choice = int(input("Select number: "))
        return matches[choice - 1]


def select_location():

    print("\nChoose Location Method")
    print("1. Search District")
    print("2. Live Location")

    choice = input("Enter choice (1/2): ")

    # -----------------------
    # SEARCH DISTRICT OPTION
    # -----------------------
    if choice == "1":
        return search_district()

    # -----------------------
    # LIVE LOCATION OPTION
    # -----------------------
    elif choice == "2":
        try:
            print("📍 Detecting live location...")
            loc = requests.get("https://ipinfo.io", timeout=5).json()
            city = loc.get("city")

            if not city:
                raise Exception("City not found")

            print("Detected City:", city)
            return city

        except Exception as e:
            print("⚠ Live location failed.")
            print("Reason:", e)
            print("Switching to manual district selection...\n")
            return search_district()

    else:
        print("Invalid choice. Using district search.")
        return search_district()


def get_weather(city):

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city},IN&appid={API_KEY}&units=metric"
    data = requests.get(url).json()

    rain = data.get("rain", {}).get("1h", 0)

    return {
        "city": city,
        "temp": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "pressure": data["main"]["pressure"],
        "wind": data["wind"]["speed"],
        "rain": rain,
        "desc": data["weather"][0]["description"]
    }


def get_weather_forecast(city):

    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city},IN&appid={API_KEY}&units=metric"
    data = requests.get(url).json()

    forecast = []

    for i in range(0, 40, 8):
        item = data["list"][i]
        forecast.append({
            "date": item["dt_txt"].split()[0],
            "temp": item["main"]["temp"],
            "humidity": item["main"]["humidity"],
            "rain": item.get("rain", {}).get("3h", 0)
        })

    return forecast
