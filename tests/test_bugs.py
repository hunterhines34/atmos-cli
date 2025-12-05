import pytest
from click.testing import CliRunner
from unittest.mock import patch
import requests
from atmos_cli.api import get_weather_data
from atmos_cli.main import cli

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture
def mock_api_calls():
    with (
        patch('atmos_cli.main.get_weather_data') as mock_get_weather_data,
        patch('atmos_cli.main.get_location_coordinates') as mock_get_location_coordinates
    ):
        yield mock_get_weather_data, mock_get_location_coordinates

# Bug 1: API Double Logging (FIXED verification)
def test_api_double_logging(capsys):
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.HTTPError("404 Not Found")

        # Call the API function
        result = get_weather_data({"latitude": 0, "longitude": 0})

        # Capture stdout
        captured = capsys.readouterr()

        # Verify it DOES NOT print to stdout (Fixed)
        assert "HTTP error occurred: 404 Not Found" not in captured.out

        # Verify it returns the error
        assert "error" in result
        assert "404 Not Found" in result["error"]

# Bug 2: Date Range Ignored
def test_start_date_ignored_without_end_date(runner, mock_api_calls):
    mock_get_weather_data, mock_get_location_coordinates = mock_api_calls
    mock_get_location_coordinates.return_value = {"latitude": 52.52, "longitude": 13.41, "name": "Berlin"}
    mock_get_weather_data.return_value = {}

    # Invoke with only start-date
    result = runner.invoke(cli, ["forecast", "--location", "Berlin", "--start-date", "2023-01-01"])

    # Verification of fix:
    assert result.exit_code != 0
    assert "Both --start-date and --end-date must be provided" in result.output

# Bug 3: Exit Code 0 on Error
def test_exit_code_on_error(runner, mock_api_calls):
    mock_get_weather_data, mock_get_location_coordinates = mock_api_calls

    # Mock invalid location error
    mock_get_location_coordinates.return_value = {"error": "Location not found"}

    result = runner.invoke(cli, ["forecast", "--location", "InvalidPlace"])

    # It prints Error
    assert "Error:" in result.output
    # Expect non-zero exit code (Fixed behavior)
    assert result.exit_code != 0

# Bug 4: Parameter Validation (Forecast Days)
def test_forecast_days_out_of_range(runner, mock_api_calls):
    mock_get_weather_data, mock_get_location_coordinates = mock_api_calls
    mock_get_location_coordinates.return_value = {"latitude": 52.52, "longitude": 13.41, "name": "Berlin"}
    mock_get_weather_data.return_value = {}

    # Invoke with out-of-range forecast days (limit is 16)
    result = runner.invoke(cli, ["forecast", "--location", "Berlin", "--forecast-days", "20"])

    # Expect validation failure (Fixed behavior)
    assert result.exit_code != 0
    # Click validation message
    assert "Invalid value for '--forecast-days'" in result.output
