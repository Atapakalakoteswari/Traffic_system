import requests
import json

API_KEY = 'eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImQ2MDIxY2EwNWY1ZjFmNWUxZTViMTMyZWY0YTQ4MmUyNzYxYTc3NmEyZmI5MGZkZmJlMWRlZmE5IiwiaCI6Im11cm11cjY0In0='  # Your complete key from screenshot

coordinates = [[72.8777, 19.0760], [73.8567, 18.5204]]

url = "https://api.openrouteservice.org/v2/directions/driving-car"
headers = {'Authorization': API_KEY, 'Content-Type': 'application/json'}
body = {"coordinates": coordinates}

print("Testing your ORS API Key...")
response = requests.post(url, json=body, headers=headers)

if response.status_code == 200:
    print("SUCCESS! Your API key is working!")
    data = response.json()
    
    print(f"\nResponse keys: {data.keys()}")
    
    if 'routes' in data:
        route = data['routes'][0]
        distance = route['distance'] / 1000
        duration = route['duration'] / 60
        print(f"\nREAL ROUTE DATA:")
        print(f"   Distance: {distance:.1f} km")
        print(f"   Duration: {duration:.1f} minutes")
        print(f"   Route name: {route.get('summary', 'N/A')}")
        
    elif 'features' in data:
        route = data['features'][0]
        distance = route['properties']['segments'][0]['distance'] / 1000
        duration = route['properties']['segments'][0]['duration'] / 60
        print(f"\nREAL ROUTE DATA:")
        print(f"   Distance: {distance:.1f} km")
        print(f"   Duration: {duration:.1f} minutes")
        
    else:
        print(f"\nRaw response (first 500 chars):")
        print(json.dumps(data, indent=2)[:500])
        
    print("\nYour system WILL show real routes!")
    
else:
    print(f"Failed: {response.status_code}")
    print(response.text)