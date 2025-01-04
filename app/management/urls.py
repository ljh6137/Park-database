from django.urls import path
from django.urls import re_path
# from django.conf.urls import url
from . import views



urlpatterns = [
    path('rented_vehicles/', views.rented_vehicles_view, name='rented_vehicles'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('rent_car/', views.rent_car_view, name='rent_car'),
    path('ui/', views.ui, name='ui'),    
    path('get-vehicles/', views.get_vehicles, name='get_vehicles'),
    path('get-vehicle-details/', views.get_vehicle_details, name='get_vehicle_details'),
    path('', views.homepage, name='homepage'),
    path('lease-vehicle/', views.lease_vehicle, name='lease_vehicle'),
    path('return_vehicle/', views.return_vehicle, name='return_vehicle'),
]
