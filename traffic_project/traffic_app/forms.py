from django import forms
from .models import TrafficPrediction
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class TrafficPredictionForm(forms.ModelForm):
    class Meta:
        model = TrafficPrediction
        fields = ['hour', 'day_of_week', 'month', 'is_weekend', 'is_rush_hour',
                 'weather', 'temperature', 'precipitation', 'road_construction',
                 'accident', 'traffic_volume']
        
        widgets = {
            'hour': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': 0, 
                'max': 23,
                'placeholder': '0-23'
            }),
            'day_of_week': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': 0, 
                'max': 6,
                'placeholder': '0=Monday, 6=Sunday'
            }),
            'month': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': 1, 
                'max': 12,
                'placeholder': '1-12'
            }),
            'is_weekend': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_rush_hour': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'weather': forms.Select(attrs={'class': 'form-control'}),
            'temperature': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.1',
                'placeholder': 'Temperature in °C'
            }),
            'precipitation': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01',
                'placeholder': 'Precipitation in mm'
            }),
            'road_construction': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'accident': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'traffic_volume': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Vehicles per hour'
            }),
        }

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user