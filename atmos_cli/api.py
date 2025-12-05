import requests
from atmos_cli.constants import OPEN_METEO_BASE_URL, ARCHIVE_BASE_URL, GEOCODING_API_URL

def get_weather_data(params: dict, archive: bool = False) -> dict:
    """Fetches weather data from the Open-Meteo API.

    This function constructs a request to the Open-Meteo forecast or archive API
    based on the provided parameters. It handles HTTP errors and other exceptions,
    returning a dictionary with an error message if something goes wrong.

    Args:
        params (dict): A dictionary of query parameters for the API request.
            Common keys include 'latitude', 'longitude', 'hourly', 'daily',
            'current_weather', 'temperature_unit', 'wind_speed_unit', etc.
        archive (bool): If True, fetches data from the archive API endpoint.
            If False, fetches data from the forecast API endpoint. Defaults to False.

    Returns:
        dict: The JSON response from the API containing weather data.
            If an error occurs, returns a dictionary with an "error" key
            containing the error message.
    """
    base_url = ARCHIVE_BASE_URL if archive else OPEN_METEO_BASE_URL
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        return {"error": str(http_err)}
    except requests.exceptions.ConnectionError as conn_err:
        return {"error": str(conn_err)}
    except requests.exceptions.Timeout as timeout_err:
        return {"error": str(timeout_err)}
    except requests.exceptions.RequestException as req_err:
        return {"error": str(req_err)}

def get_location_coordinates(location_name: str) -> dict:
    """Fetches latitude and longitude for a given location name using the Open-Meteo Geocoding API.

    This function queries the Open-Meteo Geocoding API to find the coordinates
    for a specified location name. It returns the first result found.

    Args:
        location_name (str): The name of the city, state, or country to search for.

    Returns:
        dict: A dictionary containing the location details if successful.
            The dictionary includes:
            - 'latitude' (float): The latitude of the location.
            - 'longitude' (float): The longitude of the location.
            - 'name' (str): The name of the location returned by the API.

            If the location is not found or an error occurs, returns a dictionary
            with an "error" key containing the error message.
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
