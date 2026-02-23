"""
Weather service — pure functions, no CLI input.
Wraps OpenWeatherMap API.
"""
import requests
from flask import current_app

DISTRICTS = sorted([
    "Adilabad", "Bhadradri Kothagudem", "Hanumakonda", "Hyderabad",
    "Jagtial", "Jangaon", "Jayashankar Bhupalpally", "Jogulamba Gadwal",
    "Kamareddy", "Karimnagar", "Khammam", "Komaram Bheem Asifabad",
    "Mahabubabad", "Mahabubnagar", "Mancherial", "Medak",
    "Medchal-Malkajgiri", "Mulugu", "Nagarkurnool", "Nalgonda",
    "Narayanpet", "Nirmal", "Nizamabad", "Peddapalli",
    "Rajanna Sircilla", "Rangareddy", "Sangareddy",
    "Siddipet", "Suryapet", "Vikarabad", "Wanaparthy",
    "Warangal", "Yadadri Bhuvanagiri",
])

# District name mapping for OpenWeatherMap API compatibility
DISTRICT_MAPPING = {
    "bhadradri kothagudem": "Kothagudem",
    "jayashankar bhupalpally": "Bhupalpally",
    "jogulamba gadwal": "Gadwal",
    "komaram bheem asifabad": "Asifabad",
    "medchal-malkajgiri": "Medchal",
    "rajanna sircilla": "Sircilla",
    "yadadri bhuvanagiri": "Bhuvanagiri",
    "rangareddy": "Hyderabad",  # Use nearby major city
    "hanumakonda": "Warangal",  # Use nearby major city
    "mulugu": "Warangal",  # Use nearby major city
    # Common misspellings
    "jongoan": "Jangaon",
    "jongaon": "Jangaon",
    "jongan": "Jangaon",
}


def get_weather(city: str = None, lat: float = None, lon: float = None) -> dict:
    """
    Fetch current weather for a city in Telangana, India OR by coordinates.
    
    Args:
        city: City name (optional if lat/lon provided)
        lat: Latitude (optional, for live location)
        lon: Longitude (optional, for live location)
    
    Returns dict with keys: city, temp, humidity, pressure, wind, rain, desc.
    Raises ValueError with user-friendly message if city not found or API fails.
    """
    api_key = current_app.config["WEATHER_API_KEY"]
    base_url = current_app.config["WEATHER_BASE_URL"]
    
    # Build URL based on input type
    if lat is not None and lon is not None:
        # Use coordinates (live location)
        url = f"{base_url}/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
        city_display = f"Location ({lat:.2f}, {lon:.2f})"
    elif city:
        # Normalize city name and check mapping
        city_normalized = city.strip().lower()
        api_city = DISTRICT_MAPPING.get(city_normalized, city.strip())
        url = f"{base_url}/weather?q={api_city},IN&appid={api_key}&units=metric"
        city_display = city
    else:
        raise ValueError("Either city name or coordinates (lat/lon) must be provided")

    try:
        resp = requests.get(url, timeout=10)
        
        # Handle 404 - City not found
        if resp.status_code == 404:
            if lat and lon:
                raise ValueError(
                    f"Weather data not available for coordinates ({lat}, {lon}). "
                    "Please try manual district selection."
                )
            else:
                suggestions = find_similar_districts(city)
                error_msg = f"Weather data not available for '{city}'."
                if suggestions:
                    error_msg += f" Did you mean: {', '.join(suggestions)}?"
                else:
                    error_msg += " Please check the spelling or try a nearby district."
                raise ValueError(error_msg)
        
        # Handle other HTTP errors
        if resp.status_code != 200:
            raise ValueError(
                f"Weather service error (code {resp.status_code}). "
                "Please try again later."
            )
        
        data = resp.json()
        
        # Additional validation
        if data.get("cod") != 200:
            raise ValueError(f"Weather API error: {data.get('message', 'Unknown error')}")

        # Get actual city name from response if using coordinates
        if lat and lon:
            city_display = data.get("name", city_display)

        return {
            "city": city_display,
            "temp": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "wind": data["wind"]["speed"],
            "rain": data.get("rain", {}).get("1h", 0),
            "desc": data["weather"][0]["description"].title(),
            "icon": data["weather"][0]["icon"],
        }
    
    except requests.exceptions.Timeout:
        raise ValueError("Weather service timeout. Please try again.")
    except requests.exceptions.ConnectionError:
        raise ValueError("Cannot connect to weather service. Check your internet connection.")
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Weather service error: {str(e)}")
    except (KeyError, IndexError) as e:
        raise ValueError(f"Invalid weather data received: {str(e)}")


def get_weather_forecast(city: str) -> list:
    """
    Fetch 5-day / 3-hour forecast and return one entry per day (5 days).
    Returns list of dicts: date, temp, humidity, rain.
    Raises ValueError with user-friendly message if city not found or API fails.
    """
    api_key = current_app.config["WEATHER_API_KEY"]
    base_url = current_app.config["WEATHER_BASE_URL"]
    
    # Normalize city name and check mapping
    city_normalized = city.strip().lower()
    api_city = DISTRICT_MAPPING.get(city_normalized, city.strip())
    
    url = f"{base_url}/forecast?q={api_city},IN&appid={api_key}&units=metric"

    try:
        resp = requests.get(url, timeout=10)
        
        # Handle 404 - City not found
        if resp.status_code == 404:
            suggestions = find_similar_districts(city)
            error_msg = f"Weather forecast not available for '{city}'."
            if suggestions:
                error_msg += f" Did you mean: {', '.join(suggestions)}?"
            else:
                error_msg += " Please check the spelling or try a nearby district."
            raise ValueError(error_msg)
        
        # Handle other HTTP errors
        if resp.status_code != 200:
            raise ValueError(
                f"Weather service error (code {resp.status_code}). "
                "Please try again later."
            )
        
        data = resp.json()

        forecast = []
        for i in range(0, min(40, len(data["list"])), 8):
            item = data["list"][i]
            forecast.append({
                "date": item["dt_txt"].split()[0],
                "temp": item["main"]["temp"],
                "humidity": item["main"]["humidity"],
                "rain": item.get("rain", {}).get("3h", 0),
            })
        return forecast
    
    except requests.exceptions.Timeout:
        raise ValueError("Weather service timeout. Please try again.")
    except requests.exceptions.ConnectionError:
        raise ValueError("Cannot connect to weather service. Check your internet connection.")
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Weather service error: {str(e)}")
    except (KeyError, IndexError) as e:
        raise ValueError(f"Invalid weather data received: {str(e)}")


def search_districts(prefix: str) -> list:
    """Return districts whose name starts with the given prefix (case-insensitive)."""
    prefix = prefix.strip().lower()
    return [d for d in DISTRICTS if d.lower().startswith(prefix)]


def find_similar_districts(city: str, max_suggestions: int = 3) -> list:
    """Find similar district names using simple string matching."""
    city_lower = city.strip().lower()
    suggestions = []
    
    # Check for partial matches
    for district in DISTRICTS:
        district_lower = district.lower()
        # Check if city is contained in district name or vice versa
        if city_lower in district_lower or district_lower in city_lower:
            suggestions.append(district)
        # Check if they start with the same letters
        elif len(city_lower) >= 3 and district_lower.startswith(city_lower[:3]):
            suggestions.append(district)
    
    return suggestions[:max_suggestions]
