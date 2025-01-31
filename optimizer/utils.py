from geopy.distance import geodesic
import pandas as pd
import config

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
    fuel_stops = []
    total_distance = route["features"][0]["properties"]["segments"][0]["distance"] / 1609.34  # Convert meters to miles
    segments = route["features"][0]["geometry"]["coordinates"]
    cumulative_distance = 0

    for i in range(len(segments) - 1):
        start_coord = segments[i]
        end_coord = segments[i + 1]
        segment_distance = geodesic((start_coord[1], start_coord[0]), (end_coord[1], end_coord[0])).miles
        cumulative_distance += segment_distance

        if cumulative_distance >= max_range:
            midpoint = [(start_coord[1] + end_coord[1]) / 2, (start_coord[0] + end_coord[0]) / 2]
            nearby_stations = filter_stations(fuel_prices_df, midpoint, max_distance_from_route)

            if not nearby_stations.empty:
                cheapest_station = nearby_stations.nsmallest(1, "Retail Price").iloc[0]
                fuel_stops.append({
                    "location": [cheapest_station["Longitude"], cheapest_station["Latitude"]],
                    "station": cheapest_station["Truckstop Name"],
                    "price": cheapest_station["Retail Price"]
                })
                cumulative_distance = 0  # reset for next range

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