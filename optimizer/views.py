from rest_framework.response import Response
from rest_framework.decorators import api_view
import pandas as pd
from .services import get_route, get_route_with_waypoints
from .utils import filter_stations, get_optimal_fuel_stops
import os
import config

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
file_path =config.file_path
ORS_API_KEY = config.ORS_API_KEY
VEHICLE_RANGE = config.VEHICLE_RANGE # in miles
FUEL_EFFICIENCY = config.FUEL_EFFICIENCY  # miles per gallon
MAX_DISTANCE_FROM_ROUTE = config.MAX_DISTANCE_FROM_ROUTE  # in miles

@api_view(["GET"])
def optimize_fuel_route(request):
    """API endpoint to return optimized fuel stops along a route."""
    start = request.GET.get("start")  
    end = request.GET.get("end")     

    if not start or not end:
        return Response({"error": "Start and end locations are required."}, status=400)

    # step 1: geocode fuel station addresses
    file_path_new = os.path.join(BASE_DIR, 'optimizer', 'fuel-prices-geocoded.csv')
    fuel_prices_df_updated = pd.read_csv(file_path_new)

    # step 2: get the initial route
    route = get_route(start, end, ORS_API_KEY)
    if "error" in route:
        return Response({"error": route["error"]}, status=400)

    # step 3: find optimal fuel stops
    try:
        fuel_stops = get_optimal_fuel_stops(route, fuel_prices_df_updated, VEHICLE_RANGE, MAX_DISTANCE_FROM_ROUTE)
    except Exception as e:
        return Response({"error": f"Failed to calculate fuel stops: {str(e)}"}, status=500)

    # step 4: get the updated route with fuel stops as waypoints
    waypoints = [stop["location"] for stop in fuel_stops]  
    updated_route = get_route_with_waypoints(start, end, waypoints, ORS_API_KEY)
    if "error" in updated_route:
        return Response({"error": updated_route["error"]}, status=400)
    
    # step 5: calculate total fuel cost
    total_distance = updated_route["features"][0]["properties"]["segments"][0]["distance"] / 1609.34  # Convert meters to miles
    total_gallons = total_distance / FUEL_EFFICIENCY
    total_cost = sum(stop["price"] * (VEHICLE_RANGE / FUEL_EFFICIENCY) for stop in fuel_stops)

    return Response({
        "route": updated_route,
        "fuel_stops": fuel_stops,
        "total_cost": round(total_cost, 2)
    })