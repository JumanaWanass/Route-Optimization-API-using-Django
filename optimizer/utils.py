from geopy.distance import geodesic
import pandas as pd
from . import config

from geopy.distance import geodesic
import numpy as np
from scipy.spatial import cKDTree

from geopy.distance import geodesic
import numpy as np
from scipy.spatial import cKDTree
from joblib import Parallel, delayed

def get_optimal_fuel_stops(route, fuel_prices_df, max_range=500, max_distance_from_route=50):
    """
    Determine optimal fuel stops along the route based on vehicle range and fuel prices.
    
    Args:
        route (dict): The route data from OpenRouteService.
        fuel_prices_df (pd.DataFrame): DataFrame containing fuel station data.
        max_range (int): Maximum range of the vehicle in miles.
        max_distance_from_route (int): Maximum distance a fuel station can be from the route (in miles).
    
    Returns:
        list: A list of dictionaries containing fuel stop details.
    """
    # Extract route coordinates and convert to (lat, lon) format
    segments = route["features"][0]["geometry"]["coordinates"]
    route_coords = np.array([(coord[1], coord[0]) for coord in segments])  # (lat, lon)

    # Precompute cumulative distances for all segments
    cumulative_distances = [0]
    for i in range(1, len(route_coords)):
        distance = geodesic(route_coords[i - 1], route_coords[i]).miles
        cumulative_distances.append(cumulative_distances[-1] + distance)
    cumulative_distances = np.array(cumulative_distances)

    # Create a spatial index for fuel stations
    station_coords = fuel_prices_df[["Latitude", "Longitude"]].values
    station_tree = cKDTree(station_coords)

    # Find all fuel stations within max_distance_from_route of any point on the route
    nearby_indices = set()
    for coord in route_coords:
        indices = station_tree.query_ball_point(coord, max_distance_from_route)
        nearby_indices.update(indices)
    nearby_stations = fuel_prices_df.iloc[list(nearby_indices)]

    # Find optimal fuel stops in parallel
    def find_cheapest_station(midpoint, stations):
        distances = np.array([geodesic(midpoint, (lat, lon)).miles for lat, lon in stations[["Latitude", "Longitude"]].values])
        valid_stations = stations[distances <= max_distance_from_route]
        if not valid_stations.empty:
            return valid_stations.nsmallest(1, "Retail Price").iloc[0]
        return None

    fuel_stops = []
    current_distance = 0
    for i in range(len(route_coords)):
        if cumulative_distances[i] - current_distance >= max_range:
            midpoint = route_coords[i]
            cheapest_station = find_cheapest_station(midpoint, nearby_stations)
            if cheapest_station is not None:
                fuel_stops.append({
                    "location": [cheapest_station["Longitude"], cheapest_station["Latitude"]],
                    "station": cheapest_station["Truckstop Name"],
                    "price": cheapest_station["Retail Price"]
                })
                current_distance = cumulative_distances[i]  # reset for next range

    return fuel_stops

def filter_stations(fuel_prices_df, midpoint, max_distance):
    """Filter fuel stations within a certain distance from the midpoint."""
    nearby_stations = []
    for _, row in fuel_prices_df.iterrows():
        station_location = (row["Latitude"], row["Longitude"])
        distance = geodesic(midpoint, station_location).miles
        if distance <= max_distance:
            nearby_stations.append(row)
    return pd.DataFrame(nearby_stations)