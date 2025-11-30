import pytest
from click.testing import CliRunner
from unittest.mock import patch
from atmos_cli.main import cli

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture
def mock_api_calls():
    # Patching where it is used in main.py
    with (
        patch('atmos_cli.main.get_weather_data') as mock_get_weather_data,
        patch('atmos_cli.main.get_location_coordinates') as mock_get_location_coordinates
    ):
        yield mock_get_weather_data, mock_get_location_coordinates

def test_timezone_default_auto(runner, mock_api_calls):
    mock_get_weather_data, mock_get_location_coordinates = mock_api_calls

    mock_get_location_coordinates.return_value = {"latitude": 40.71, "longitude": -74.01, "name": "New York"}
    mock_get_weather_data.return_value = {
        "current": {"time": 0, "temperature_2m": 20},
        "timezone": "America/New_York",
        "current_units": {"temperature_2m": "C"} # Added units to avoid crash in display
    }

    # Run forecast without timezone
    result = runner.invoke(cli, ["forecast", "--location", "New York", "--current"])

    assert result.exit_code == 0

    # Verify that get_weather_data was called with timezone="auto"
    mock_get_weather_data.assert_called_once()
    call_args = mock_get_weather_data.call_args
    params = call_args[0][0] # First arg is params

    # This assertion is expected to fail before the fix if the bug exists
    assert "timezone" in params
    assert params["timezone"] == "auto"
