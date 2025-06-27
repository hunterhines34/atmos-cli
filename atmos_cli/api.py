import requests
from atmos_cli.constants import OPEN_METEO_BASE_URL, ARCHIVE_BASE_URL, GEOCODING_API_URL

def get_weather_data(params: dict, archive: bool = False) -> dict:
    """Fetches weather data from the Open-Meteo API.

    Args:
        params (dict): Dictionary of query parameters for the API request.
        archive (bool): If True, fetches from the archive API. Defaults to False.

    Returns:
        dict: JSON response from the API.
    """
    base_url = ARCHIVE_BASE_URL if archive else OPEN_METEO_BASE_URL
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return {"error": str(http_err)}
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
        return {"error": str(conn_err)}
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
        return {"error": str(timeout_err)}
    except requests.exceptions.RequestException as req_err:
        print(f"An unexpected error occurred: {req_err}")
        return {"error": str(req_err)}

def get_location_coordinates(location_name: str) -> dict:
    """Fetches latitude and longitude for a given location name using the Open-Meteo Geocoding API.

    Args:
        location_name (str): The name of the city, state, or country.

    Returns:
        dict: A dictionary containing 'latitude', 'longitude', and 'name' if successful, 
              otherwise an error dictionary.
    """
    params = {"name": location_name, "count": 1, "language": "en", "format": "json"}
    try:
        response = requests.get(GEOCODING_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        if data and data.get("results"):
            first_result = data["results"][0]
            return {
                "latitude": first_result["latitude"],
                "longitude": first_result["longitude"],
                "name": first_result.get("name", location_name)
            }
        else:
            return {"error": f"Could not find coordinates for '{location_name}'."}
    except requests.exceptions.HTTPError as http_err:
        return {"error": f"HTTP error during geocoding: {http_err}"}
    except requests.exceptions.ConnectionError as conn_err:
        return {"error": f"Connection error during geocoding: {conn_err}"}
    except requests.exceptions.Timeout as timeout_err:
        return {"error": f"Timeout error during geocoding: {timeout_err}"}
    except requests.exceptions.RequestException as req_err:
        return {"error": f"An unexpected error occurred during geocoding: {req_err}"}