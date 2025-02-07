from datetime import datetime
import requests
import pytz

# Replace with your location
latitude = 33.5779
longitude = -101.8552

# Get sunrise and sunset times from API
url = f"https://api.sunrise-sunset.org/json?lat={latitude}&lng={longitude}&formatted=0"
response = requests.get(url)
data = response.json()

# Convert UTC to local time (Lubbock, CST/CDT)
central_tz = pytz.timezone("America/Chicago")

# Extract and convert times
sunrise_utc = datetime.fromisoformat(data['results']['sunrise']).replace(tzinfo=pytz.utc)
sunset_utc = datetime.fromisoformat(data['results']['sunset']).replace(tzinfo=pytz.utc)

sunrise_local = sunrise_utc.astimezone(central_tz)
sunset_local = sunset_utc.astimezone(central_tz)

# Print local times
print(f"Sunrise (Local Time): {sunrise_local.strftime('%Y-%m-%d %I:%M:%S %p %Z')}")
print(f"Sunset (Local Time): {sunset_local.strftime('%Y-%m-%d %I:%M:%S %p %Z')}")
