import pytest
from click.testing import CliRunner
from unittest.mock import patch
from atmos_cli.main import cli

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture
def mock_api_calls():
    with (
        patch('atmos_cli.api.get_weather_data') as mock_get_weather_data,
        patch('atmos_cli.api.get_location_coordinates') as mock_get_location_coordinates
    ):
        yield mock_get_weather_data, mock_get_location_coordinates

def test_forecast_unixtime_crash(runner, mock_api_calls):
    mock_get_weather_data, mock_get_location_coordinates = mock_api_calls

    mock_get_location_coordinates.return_value = {"latitude": 52.52, "longitude": 13.41, "name": "Berlin"}

    # Mock response with unixtime (integers)
    mock_get_weather_data.return_value = {
        "timezone": "Europe/Berlin",
        "current": {
            "time": 1700000000,
            "temperature_2m": 10
        },
        "hourly": {
            "time": [1700000000, 1700003600],
            "temperature_2m": [10, 11]
        },
        "daily": {
            "time": [1700000000],
            "temperature_2m_max": [15],
            "temperature_2m_min": [5]
        },
        "current_units": {"temperature_2m": "C"},
        "hourly_units": {"temperature_2m": "C"},
        "daily_units": {"temperature_2m_max": "C"}
    }

    # Test current weather
    result = runner.invoke(cli, ["forecast", "--location", "Berlin", "--current", "--timeformat", "unixtime"])
    assert result.exit_code == 0

    # Test hourly weather
    result = runner.invoke(cli, ["forecast", "--location", "Berlin", "--hourly", "temperature_2m", "--timeformat", "unixtime"])
    assert result.exit_code == 0

    # Test daily weather
    result = runner.invoke(cli, ["forecast", "--location", "Berlin", "--daily", "temperature_2m_max", "--timeformat", "unixtime"])
    assert result.exit_code == 0
