import os
import json
import logging
import pandas as pd
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GEOAPIFY_API_KEY = "18b9061124d24ffab776900baa28638b"  

if not GEOAPIFY_API_KEY:
    logger.error("Geoapify API key is missing. Set GEOAPIFY_API_KEY as an environment variable.")
    exit(1)

file_path = os.path.join(BASE_DIR, 'fuel-prices-for-be-assessment.csv')
output_file = os.path.join(BASE_DIR, "fuel-prices-geocoded.csv")
CACHE_FILE = os.path.join(BASE_DIR, "geocode_cache.json")


geocode_cache = {}
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r") as f:
        geocode_cache = json.load(f)

def get_api_response_batch(addresses):
    """Send batch request to Geoapify Geocoding API and return job ID."""
    base_url = "https://api.geoapify.com/v1/batch/geocode/search"
    headers = {'Content-Type': 'application/json'}

    # prepare batch payload as an array of address strings
    data = addresses  
    params = {"apiKey": GEOAPIFY_API_KEY}

    logger.info(f"Sending batch request with {len(addresses)} addresses")
    try:
        response = requests.post(base_url, headers=headers, params=params, json=data, timeout=30)
        response.raise_for_status()
        logger.info("Batch request successful. Job ID received.")
        return response.json()  # returns job ID and status URL
    except requests.RequestException as e:
        logger.error(f"Batch API request failed: {e}")
        logger.error(f"Response content: {response.content if 'response' in locals() else 'No response'}")
        return None

def poll_for_results(job_id):
    """Poll the API for batch geocoding results."""
    base_url = f"https://api.geoapify.com/v1/batch/geocode/search?id={job_id}&apiKey={GEOAPIFY_API_KEY}"
    while True:
        try:
            response = requests.get(base_url, timeout=30)
            response.raise_for_status()
            results = response.json()
            if isinstance(results, list):  
                logger.info("Batch results retrieved successfully.")
                return results
            elif results.get("status") == "pending":  
                logger.info("Results are pending. Retrying in 10 seconds...")
                time.sleep(10)
            else:
                logger.error(f"Unexpected response: {results}")
                return None
        except requests.RequestException as e:
            logger.error(f"Error polling for results: {e}")
            return None

def parse_address(row):
    """Extracts full address as a single string."""
    return f"{row['Address']}, {row['City']}, {row['State']}, USA"

def preprocess(batch_size=100, num_threads=5):
    """Parallel batch geocoding with caching."""
    fuel_prices_df = pd.read_csv(file_path)

    # make sure Latitude and Longitude columns exist
    if "Latitude" not in fuel_prices_df.columns:
        fuel_prices_df["Latitude"] = None
    if "Longitude" not in fuel_prices_df.columns:
        fuel_prices_df["Longitude"] = None

    # extract unique addresses
    unique_addresses = {parse_address(row): None for _, row in fuel_prices_df.iterrows()}
    logger.info(f"Total unique addresses to geocode: {len(unique_addresses)}")

    # split into batches
    addresses_list = list(unique_addresses.keys())
    batches = [addresses_list[i:i + batch_size] for i in range(0, len(addresses_list), batch_size)]
    logger.info(f"Processing {len(batches)} batches with {num_threads} threads")

    # use threads to process batches in parallel
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        future_to_batch = {executor.submit(get_api_response_batch, batch): batch for batch in batches}
        for i, future in enumerate(as_completed(future_to_batch)):
            try:
                job_info = future.result()
                if job_info and "id" in job_info:
                    job_id = job_info["id"]
                    results = poll_for_results(job_id)
                    if results:
                        for result in results:
                            address = result["query"]["text"]
                            if "lon" in result and "lat" in result:
                                lon, lat = result["lon"], result["lat"]
                                geocode_cache[address] = (lon, lat)
                            else:
                                geocode_cache[address] = (None, None)
                                logger.warning(f"No coordinates found for {address}")
                logger.info(f"Completed batch {i + 1}/{len(batches)}")
            except Exception as e:
                logger.error(f"Error processing batch: {e}")

    # save updated cache
    with open(CACHE_FILE, "w") as f:
        json.dump(geocode_cache, f)

    # assign geocoded results back to DataFrame
    for index, row in fuel_prices_df.iterrows():
        address = parse_address(row)
        if address in geocode_cache:
            lon, lat = geocode_cache[address]
            fuel_prices_df.at[index, "Longitude"] = lon
            fuel_prices_df.at[index, "Latitude"] = lat

    # remove rows with missing coordinates and save
    fuel_prices_df.dropna(subset=["Latitude", "Longitude"], inplace=True)
    fuel_prices_df.to_csv(output_file, index=False)
    logger.info(f"Geocoding complete. Results saved to {output_file}")

if __name__ == "__main__":
    preprocess(batch_size=100, num_threads=5)
    # only 113 missing addresses 