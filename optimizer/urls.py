from django.urls import path
from .views import optimize_fuel_route

urlpatterns = [
    path('optimize-route/', optimize_fuel_route, name='optimize_fuel_route'),
]
