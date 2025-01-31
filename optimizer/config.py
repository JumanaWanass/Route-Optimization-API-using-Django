import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
file_path = os.path.join(BASE_DIR, 'optimizer', 'fuel-prices-for-be-assessment.csv')
ORS_API_KEY = "5b3ce3597851110001cf624895ff066137134ab38cf16c184105754f"

VEHICLE_RANGE = 500  # in miles
FUEL_EFFICIENCY = 10  # miles per gallon
MAX_DISTANCE_FROM_ROUTE = 50  # in miles

ORS_DIRECTIONS_URL = "https://api.openrouteservice.org/v2/directions/cycling-road"
