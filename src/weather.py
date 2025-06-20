import requests

# Your WeatherAPI key
API_KEY = "f558fed02341452088c41827252006"  # <-- Replace with your actual API key

# Input city name
city = "Kannur"

# Build the API request URL
url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}"

# Send GET request
response = requests.get(url)

# Parse JSON data
if response.status_code == 200:
    data = response.json()
    location = data['location']
    current = data['current']
    
    print(f"\nWeather in {location['name']}, {location['region']}, {location['country']}")
    print(f"Local Time     : {location['localtime']}")
    print(f"Temperature    : {current['temp_c']}°C")
    print(f"Feels Like     : {current['feelslike_c']}°C")
    print(f"Condition      : {current['condition']['text']}")
    print(f"Wind Speed     : {current['wind_kph']} kph")
    print(f"Humidity       : {current['humidity']}%")
    print(f"Cloud Cover    : {current['cloud']}%")
else:
    print(f"Failed to get data. Status Code: {response.status_code}")
    print(response.text)
