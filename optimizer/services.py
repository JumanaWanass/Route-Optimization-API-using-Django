import requests
from . import config

ORS_DIRECTIONS_URL = config.ORS_DIRECTIONS_URL


def get_route(start, end, ORS_API_KEY):
    """Fetch route from OpenRouteService API."""
    headers = {
        "Authorization": ORS_API_KEY,
    }
    params = {
        "start": start,
        "end": end
    }
    url = f"{ORS_DIRECTIONS_URL}?api_key={ORS_API_KEY}&start={start}&end={end}"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return {"error": f"Failed to fetch route: {response.text}"}

    return response.json()

def get_route_with_waypoints(start, end, waypoints, ORS_API_KEY):
    """Fetch route from OpenRouteService API with waypoints."""
    headers = {
        "Authorization": ORS_API_KEY,
    }
    params = {
        "start": start,
        "end": end,
        "waypoints": waypoints
    }
    url = f"{ORS_DIRECTIONS_URL}?api_key={ORS_API_KEY}&start={start}&end={end}&waypoints={waypoints}"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return {"error": f"Failed to fetch route: {response.text}"}

    return response.json()