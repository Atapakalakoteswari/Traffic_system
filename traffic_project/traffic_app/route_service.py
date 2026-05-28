import math
import random
from datetime import datetime

class RouteService:
    @staticmethod
    def calculate_route_options(start_lat, start_lng, end_lat, end_lng):
        """Calculate multiple route options with estimated times"""
        distance = RouteService.calculate_distance(start_lat, start_lng, end_lat, end_lng)
        current_hour = datetime.now().hour
        is_rush_hour = current_hour in [7, 8, 9, 17, 18, 19]
        
        routes = []
        
        fastest_time = RouteService.calculate_travel_time(distance, is_rush_hour, 'fastest')
        routes.append({
            'type': 'fastest',
            'name': 'Fastest Route',
            'distance': distance,
            'duration': fastest_time,
            'congestion': 'High' if is_rush_hour else 'Low',
            'color': '#007bff',
            'icon': 'rocket'
        })
        
        shortest_time = RouteService.calculate_travel_time(distance, is_rush_hour, 'shortest')
        routes.append({
            'type': 'shortest',
            'name': 'Shortest Route',
            'distance': distance * 0.9,
            'duration': shortest_time,
            'congestion': 'Medium',
            'color': '#28a745',
            'icon': 'ruler'
        })
        
        eco_time = RouteService.calculate_travel_time(distance, is_rush_hour, 'eco')
        routes.append({
            'type': 'eco',
            'name': 'Eco-Friendly Route',
            'distance': distance * 1.1,
            'duration': eco_time,
            'congestion': 'Low',
            'color': '#20c997',
            'icon': 'leaf'
        })
        
        return routes
    
    @staticmethod
    def calculate_distance(lat1, lng1, lat2, lng2):
        """Calculate distance between two points using Haversine formula"""
        R = 6371  # Earth's radius in km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    @staticmethod
    def calculate_travel_time(distance, is_rush_hour, route_type):
        """Calculate estimated travel time in minutes"""
        # Base speeds in km/h
        speeds = {
            'fastest': 50,
            'shortest': 45,
            'eco': 40
        }
        
        speed = speeds.get(route_type, 45)
        
        # Apply traffic factor
        if is_rush_hour:
            speed *= 0.6
        else:
            speed *= 0.9
        
        time_minutes = (distance / speed) * 60
        time_minutes *= random.uniform(0.95, 1.05)
        return round(time_minutes, 1)