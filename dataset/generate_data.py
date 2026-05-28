import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

np.random.seed(42)
random.seed(42)

def generate_traffic_data(n_samples=10000):
    """Generate synthetic traffic data"""
    data = []
    start_date = datetime(2023, 1, 1, 0, 0, 0)
    
    for i in range(n_samples):
        # Time features
        date = start_date + timedelta(hours=i)
        hour = date.hour
        day_of_week = date.weekday()
        month = date.month
        is_weekend = 1 if day_of_week >= 5 else 0
        is_rush_hour = 1 if (7 <= hour <= 9) or (17 <= hour <= 19) else 0
        
        # Weather conditions
        weather_options = ['Clear', 'Rain', 'Fog', 'Snow', 'Cloudy']
        weather = random.choice(weather_options)
        temperature = np.random.normal(20, 10)
        precipitation = np.random.exponential(0.5) if weather in ['Rain', 'Snow'] else 0
        
        road_construction = 1 if random.random() < 0.05 else 0  # 5% chance
        accident = 1 if random.random() < 0.02 else 0  # 2% chance
        
        base_volume = 500
        if is_rush_hour:
            base_volume += random.randint(300, 700)
        if is_weekend:
            base_volume -= random.randint(100, 300)
        if weather in ['Rain', 'Snow']:
            base_volume -= random.randint(50, 150)
        if accident:
            base_volume -= random.randint(100, 300)
            
        traffic_volume = max(100, base_volume + np.random.normal(0, 50))
        
        # Speed (km/h)
        base_speed = 60
        if is_rush_hour:
            base_speed -= random.randint(10, 30)
        if traffic_volume > 800:
            base_speed -= random.randint(15, 35)
        if weather == 'Rain':
            base_speed -= random.randint(5, 15)
        elif weather == 'Snow':
            base_speed -= random.randint(10, 25)
        elif weather == 'Fog':
            base_speed -= random.randint(5, 20)
        if accident:
            base_speed -= random.randint(20, 40)
            
        speed = max(10, base_speed + np.random.normal(0, 10))
        
        if speed > 50:
            congestion = 0
        elif speed > 35:
            congestion = 1
        elif speed > 20:
            congestion = 2
        else:
            congestion = 3
            
        travel_time = (10 / speed) * 60
        
        data.append({
            'hour': hour,
            'day_of_week': day_of_week,
            'month': month,
            'is_weekend': is_weekend,
            'is_rush_hour': is_rush_hour,
            'weather': weather,
            'temperature': round(temperature, 1),
            'precipitation': round(precipitation, 2),
            'road_construction': road_construction,
            'accident': accident,
            'traffic_volume': round(traffic_volume),
            'speed': round(speed, 1),
            'congestion_level': congestion,
            'travel_time': round(travel_time, 1)
        })
    
    return pd.DataFrame(data)

if __name__ == "__main__":
    print("="*60)
    print("Generating Traffic Dataset")
    print("="*60)
    
    print("\n Generating 10,000 traffic records...")
    df = generate_traffic_data(10000)
    
    df.to_csv('traffic_data.csv', index=False)
    
    print(f"\nDataset created successfully!")
    print(f"Total records: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    
    print("\nSample data (first 5 rows):")
    print(df.head())
    
    print("\nDataset statistics:")
    print(df.describe())
    
    print("\nCongestion level distribution:")
    congestion_counts = df['congestion_level'].value_counts().sort_index()
    for level, count in congestion_counts.items():
        level_name = ['Low', 'Medium', 'High', 'Severe'][level]
        percentage = (count / len(df)) * 100
        print(f"   {level_name}: {count} ({percentage:.1f}%)")
    
    print("\nWeather distribution:")
    weather_counts = df['weather'].value_counts()
    for weather, count in weather_counts.items():
        percentage = (count / len(df)) * 100
        print(f"   {weather}: {count} ({percentage:.1f}%)")
    
    print("\nDataset saved as 'traffic_data.csv'")
    print("="*60)