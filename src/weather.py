import requests
import sys
import json
# Your WeatherAPI key
API_KEY = "f558fed02341452088c41827252006"  # <-- Replace with your actual API key

if len(sys.argv) < 2:
    print("No city provided.")
    sys.exit(1)

city = sys.argv[1]

# Build the API request URL
url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}"

# Send GET request
response = requests.get(url)

# Parse JSON data
if response.status_code == 200:
    data = response.json()
    location = data['location']
    current = data['current']
    
    weather_data = {
        "city": location['name'],
        "local_time": location['localtime'],
        "temp_c": current['temp_c'],
        "feelslike_c": current['feelslike_c'],
        "condition": current['condition']['text']
    }

    print(json.dumps(weather_data))  # 👈 Output as JSON string
else:
    print(json.dumps({ "error": f"Weather fetch failed for {city}", "status": response.status_code }))
