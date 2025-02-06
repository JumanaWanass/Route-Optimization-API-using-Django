# Route Optimization API using Django

## Overview
This Django-based API provides optimized routes for fuel-efficient travel. It determines the best route between a given start and end location while considering optimal fuel stops to minimize total cost.

## Features
- **Route Optimization**: Calculates the shortest and most cost-efficient route using a Greedy approach.
- **Fuel Stop Selection**: Determines optimal refueling stations based on price, distance, and vehicle range.
- **Geocoding Preprocessing**: Enriches datasets by adding latitude and longitude to stations lacking coordinates.

## Project Structure
```
Route-Optimization-API-using-Django/
│── fuel_optimizer/             # Django project settings
│── optimizer/                  # Core application logic
│   ├── views.py                # API endpoints
│   ├── services.py             # Route fetching logic
│   ├── utils.py                # Helper functions
│── requirements.txt            # Dependencies
│── manage.py                   # Django project manager
```

## Setup Instructions
### Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/JumanaWanass/Route-Optimization-API-using-Django.git
   cd Route-Optimization-API-using-Django
   ```

2. **Set up a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Run the development server:**
   ```bash
   python manage.py runserver
   ```
   Access the API at `http://127.0.0.1:8000/`

---
## Data Preprocessing
### Problem:
The original dataset did not include latitude and longitude for fuel stations, making geospatial calculations impossible.

### Solution:
The `preprocess_stations.py` script utilizes the Geoapify API to batch geocode missing coordinates. It:
1. Extracts unique addresses from the dataset.
2. Sends them to the Geoapify API in batches.
3. Caches results to avoid redundant API calls.
4. Saves the updated dataset (`fuel-prices-geocoded.csv`) for optimization use.

#### How to Run:
```bash
python preprocess_stations.py
```

---
## Route Optimization Logic
### 1. **Fetching the Initial Route**
- The API calls OpenRouteService (ORS) to get a basic route from the start to the end location.
- Implemented in `services.py`:
  ```python
  def get_route(start, end, ORS_API_KEY):
      url = f"{ORS_DIRECTIONS_URL}?api_key={ORS_API_KEY}&start={start}&end={end}"
      response = requests.get(url)
      return response.json() if response.status_code == 200 else {"error": response.text}
  ```

### 2. **Fuel Stop Selection (Greedy Approach)**
- The optimizer selects fuel stops that minimize total cost while ensuring the vehicle does not run out of fuel.
- Implemented in `utils.py`:
  - Filters fuel stations within a certain distance of the route.
  - Sorts stations by price.
  - Selects stations greedily to refuel as efficiently as possible.

### 3. **Generating the Final Route with Waypoints**
- The updated route includes selected fuel stations as waypoints.
- Implemented in `services.py`:
  ```python
  def get_route_with_waypoints(start, end, waypoints, ORS_API_KEY):
      url = f"{ORS_DIRECTIONS_URL}?api_key={ORS_API_KEY}&start={start}&end={end}&waypoints={waypoints}"
      response = requests.get(url)
      return response.json() if response.status_code == 200 else {"error": response.text}
  ```

---
## API Usage
### **Endpoint: Optimize Fuel Route**
**URL:** `/optimize-fuel-route`

**Method:** `GET`

**Parameters:**
- `start` (string) - Starting location.
- `end` (string) - Destination.

**Response:**
```json
{
  "route": { ... },
  "fuel_stops": [ {"location": "lat,lon", "price": 3.50}, ... ],
  "total_cost": 45.30
}
```
