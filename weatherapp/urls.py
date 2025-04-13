from django.urls import path
from . import views

urlpatterns = [
    path('get_weather_by_coords/', views.get_weather_by_coords, name='get_weather_by_coords'),
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('save_city/', views.save_city, name='save_city'),
    path('remove_city/<int:city_id>/', views.remove_city, name='remove_city'),
    path('update_city/<int:city_id>/', views.update_city, name='update_city'),
    path('logout/', views.logout_view, name='logout'),
]