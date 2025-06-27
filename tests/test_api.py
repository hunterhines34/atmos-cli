import pytest
import requests
from unittest.mock import patch
from atmos_cli.api import get_weather_data, get_location_coordinates

# Mock data for successful API responses
MOCK_WEATHER_DATA = {
    "latitude": 52.52,
    "longitude": 13.41,
    "generationtime_ms": 0.123,
    "utc_offset_seconds": 7200,
    "timezone": "Europe/Berlin",
    "timezone_abbreviation": "CEST",
    "elevation": 38.0,
    "current_units": {"time": "iso8601", "temperature_2m": "°F"},
    "current": {"time": "2023-10-27T10:00", "temperature_2m": 55.0},
    "daily_units": {"time": "iso8601", "temperature_2m_max": "°F", "temperature_2m_min": "°F"},
    "daily": {
        "time": ["2023-10-27", "2023-10-28"],
        "temperature_2m_max": [60.0, 58.0],
        "temperature_2m_min": [50.0, 48.0]
    }
}

MOCK_GEOCODING_DATA = {
    "results": [
        {
            "id": 1,
            "name": "Berlin",
            "latitude": 52.52,
            "longitude": 13.41,
            "elevation": 38.0,
            "feature_code": "PPLC",
            "country_code": "DE",
            "timezone": "Europe/Berlin",
            "population": 3426354,
            "country_id": 2921044,
            "country": "Germany",
            "admin1": "Berlin",
            "admin2": "",
            "admin3": ""
        }
    ]
}

# Test get_weather_data
@patch('requests.get')
def test_get_weather_data_success(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = MOCK_WEATHER_DATA
    mock_get.return_value.raise_for_status.return_value = None

    params = {"latitude": 52.52, "longitude": 13.41}
    data = get_weather_data(params)
    assert data == MOCK_WEATHER_DATA
    mock_get.assert_called_once()

@patch('requests.get')
def test_get_weather_data_http_error(mock_get):
    mock_get.return_value.status_code = 404
    mock_get.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")

    params = {"latitude": 52.52, "longitude": 13.41}
    data = get_weather_data(params)
    assert "error" in data
    assert "404 Not Found" in data["error"]

@patch('requests.get')
def test_get_weather_data_connection_error(mock_get):
    mock_get.side_effect = requests.exceptions.ConnectionError("Network unreachable")

    params = {"latitude": 52.52, "longitude": 13.41}
    data = get_weather_data(params)
    assert "error" in data
    assert "Network unreachable" in data["error"]

@patch('requests.get')
def test_get_weather_data_timeout_error(mock_get):
    mock_get.side_effect = requests.exceptions.Timeout("Request timed out")

    params = {"latitude": 52.52, "longitude": 13.41}
    data = get_weather_data(params)
    assert "error" in data
    assert "Request timed out" in data["error"]

@patch('requests.get')
def test_get_weather_data_generic_request_exception(mock_get):
    mock_get.side_effect = requests.exceptions.RequestException("Something went wrong")

    params = {"latitude": 52.52, "longitude": 13.41}
    data = get_weather_data(params)
    assert "error" in data
    assert "Something went wrong" in data["error"]

@patch('requests.get')
def test_get_weather_data_archive(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = MOCK_WEATHER_DATA
    mock_get.return_value.raise_for_status.return_value = None

    params = {"latitude": 52.52, "longitude": 13.41}
    data = get_weather_data(params, archive=True)
    assert data == MOCK_WEATHER_DATA
    # Verify that the archive URL was called
    assert "archive-api.open-meteo.com" in mock_get.call_args[0][0]

# Test get_location_coordinates
@patch('requests.get')
def test_get_location_coordinates_success(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = MOCK_GEOCODING_DATA
    mock_get.return_value.raise_for_status.return_value = None

    location = "Berlin"
    coords = get_location_coordinates(location)
    assert coords["latitude"] == 52.52
    assert coords["longitude"] == 13.41
    assert coords["name"] == "Berlin"
    mock_get.assert_called_once()

@patch('requests.get')
def test_get_location_coordinates_not_found(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"results": []}
    mock_get.return_value.raise_for_status.return_value = None

    location = "NonExistentCity"
    coords = get_location_coordinates(location)
    assert "error" in coords
    assert "Could not find coordinates" in coords["error"]

@patch('requests.get')
def test_get_location_coordinates_http_error(mock_get):
    mock_get.return_value.status_code = 400
    mock_get.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError("400 Bad Request")

    location = "InvalidLocation"
    coords = get_location_coordinates(location)
    assert "error" in coords
    assert "400 Bad Request" in coords["error"]
