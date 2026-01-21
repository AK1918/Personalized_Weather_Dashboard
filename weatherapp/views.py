from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.conf import settings
from django.http import JsonResponse
from .models import City
import requests

def home(request):
    return render(request, 'weatherapp/home.html')

def get_weather_by_coords(request):
    lat = request.GET.get('lat')
    lon = request.GET.get('lon')
    
    if not lat or not lon:
        return JsonResponse({'error': 'Latitude and longitude are required'}, status=400)
    
    # Get more accurate location name using reverse geocoding
    geocoding_url = f'http://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&limit=1&appid={settings.OPENWEATHER_API_KEY}'
    
    try:
        # First get the accurate location name
        geo_response = requests.get(geocoding_url)
        geo_response.raise_for_status()
        location_data = geo_response.json()
        
        if not location_data:
            return JsonResponse({'error': 'Location not found'}, status=404)
            
        # Get weather data
        weather_url = f'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={settings.OPENWEATHER_API_KEY}'
        weather_response = requests.get(weather_url)
        weather_response.raise_for_status()
        weather_data = weather_response.json()
        
        # Use the default English city name
        weather_data['name'] = location_data[0].get('name')
        
        return JsonResponse(weather_data)
        
    except requests.RequestException as e:
        return JsonResponse({'error': str(e)}, status=500)

# Add this new logout view
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged in successfully!")
    return redirect('home')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def dashboard(request):
    weather_data = []
    cities = City.objects.filter(user=request.user)
    
    for city in cities:
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city.name}&units=metric&appid={settings.OPENWEATHER_API_KEY}'  # Use settings.OPENWEATHER_API_KEY
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            data['id'] = city.id  # Add database ID for deletion
            weather_data.append(data)
    
    return render(request, 'weatherapp/dashboard.html', {'weather_data': weather_data})

@login_required
def save_city(request):
    if request.method == 'POST':
        city_name = request.POST.get('city_name')
        
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city_name}&units=metric&appid={settings.OPENWEATHER_API_KEY}'  # Use settings.OPENWEATHER_API_KEY
        response = requests.get(url)
        
        if response.status_code == 200:
            # Create city if verification successful
            try:
                City.objects.create(name=city_name, user=request.user)
                messages.success(request, f'{city_name} has been added successfully!')
            except Exception:
                messages.error(request, f'{city_name} is already in your list!')
        else:
            messages.error(request, 'City not found!')
    
    return redirect('dashboard')

@login_required
def remove_city(request, city_id):
    try:
        city = City.objects.get(id=city_id, user=request.user)
        city_name = city.name
        city.delete()
        messages.success(request, f'{city_name} has been removed successfully!')
    except City.DoesNotExist:
        messages.error(request, 'City not found!')
    
    return redirect('dashboard')

@login_required
def update_city(request, city_id):
    if request.method == 'POST':
        new_name = request.POST.get('city_name')
        try:
            city = City.objects.get(id=city_id, user=request.user)
            
            # Verify new city name exists in OpenWeather
            url = f'http://api.openweathermap.org/data/2.5/weather?q={new_name}&units=metric&appid={settings.OPENWEATHER_API_KEY}'
            
            response = requests.get(url)
            
            if response.status_code == 200:
                city.name = new_name
                city.save()
                messages.success(request, f'City updated to {new_name} successfully!')
            else:
                messages.error(request, 'City not found!')
        except City.DoesNotExist:
            messages.error(request, 'City not found!')
    

    return redirect('dashboard')

