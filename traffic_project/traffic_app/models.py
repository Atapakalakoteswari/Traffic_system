from django.db import models
from django.contrib.auth.models import User

class TrafficPrediction(models.Model):
    CONGESTION_CHOICES = [
        (0, 'Low Traffic'),
        (1, 'Medium Traffic'),
        (2, 'High Traffic'),
        (3, 'Severe Traffic'),
    ]
    
    WEATHER_CHOICES = [
        ('Clear', 'Clear'),
        ('Rain', 'Rain'),
        ('Fog', 'Fog'),
        ('Snow', 'Snow'),
        ('Cloudy', 'Cloudy'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='traffic_predictions', null=True, blank=True)
    hour = models.IntegerField()
    day_of_week = models.IntegerField()
    month = models.IntegerField()
    is_weekend = models.BooleanField()
    is_rush_hour = models.BooleanField()
    weather = models.CharField(max_length=20, choices=WEATHER_CHOICES)
    temperature = models.FloatField()
    precipitation = models.FloatField()
    road_construction = models.BooleanField()
    accident = models.BooleanField()
    traffic_volume = models.IntegerField()
    predicted_congestion = models.IntegerField(choices=CONGESTION_CHOICES)
    predicted_travel_time = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Prediction on {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class RouteHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='route_histories', null=True, blank=True)
    start_location = models.CharField(max_length=255)
    end_location = models.CharField(max_length=255)
    start_lat = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    start_lng = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    end_lat = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    end_lng = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    duration_minutes = models.FloatField()
    distance_km = models.FloatField()
    congestion_level = models.IntegerField()
    route_type = models.CharField(max_length=50, default='fastest')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.start_location} → {self.end_location}"