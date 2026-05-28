from django.contrib import admin
from .models import TrafficPrediction, RouteHistory

@admin.register(TrafficPrediction)
class TrafficPredictionAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'hour', 'weather', 'traffic_volume', 'predicted_congestion', 'predicted_travel_time']
    list_filter = ['predicted_congestion', 'weather', 'is_weekend', 'is_rush_hour']
    search_fields = ['weather']
    readonly_fields = ['created_at']

@admin.register(RouteHistory)
class RouteHistoryAdmin(admin.ModelAdmin):
    list_display = ['start_location', 'end_location', 'duration_minutes', 'distance_km', 'created_at']
    list_filter = ['route_type', 'congestion_level']
    search_fields = ['start_location', 'end_location']



