from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('predict/', views.predict_traffic, name='predict'),
    path('history/', views.history, name='history'),
    path('realtime-navigation/', views.realtime_navigation, name='realtime_navigation'),
    path('calculate-route/', views.calculate_route, name='calculate_route'),
    path('get-route-history/', views.get_route_history, name='get_route_history'),
]


