import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
import os
import json

from atmos_cli.main import cli, HISTORY_FILE
from atmos_cli.constants import (
    DEFAULT_LATITUDE, DEFAULT_LONGITUDE, DEFAULT_TIMEZONE,
    TEMPERATURE_UNITS, WIND_SPEED_UNITS, PRECIPITATION_UNITS
)
from rich.table import Table # Import Table for assertion
from rich.panel import Panel # Import Panel for assertion

# Fixture for CLI runner
@pytest.fixture
def runner():
    return CliRunner()

# Fixture to mock config file operations
@pytest.fixture
def mock_config_file(tmp_path):
    config_path = tmp_path / ".atmos_cli_config.json"
    # Patch the CONFIG_FILE constant in atmos_cli.config
    with patch('atmos_cli.config.CONFIG_FILE', new=config_path):
        # Ensure the config module reloads with the patched path
        import atmos_cli.config
        atmos_cli.config.CONFIG_FILE = config_path
        yield config_path
        # Clean up history file if created during test
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)

# Fixture to mock API calls
@pytest.fixture
def mock_api_calls():
    with (
        patch('atmos_cli.api.get_weather_data') as mock_get_weather_data,
        patch('atmos_cli.api.get_location_coordinates') as mock_get_location_coordinates
    ):
        yield mock_get_weather_data, mock_get_location_coordinates

# Fixture to mock display functions
@pytest.fixture
def mock_display_functions():
    with (
        patch('atmos_cli.display.display_current_weather') as mock_current,
        patch('atmos_cli.display.display_hourly_weather') as mock_hourly,
        patch('atmos_cli.display.display_daily_weather') as mock_daily,
        patch('atmos_cli.display.display_daily_temperature_chart') as mock_chart,
        patch('atmos_cli.display.display_error') as mock_error,
        patch('atmos_cli.display.display_message') as mock_message
    ):
        yield mock_current, mock_hourly, mock_daily, mock_chart, mock_error, mock_message

# --- Test forecast command ---

def test_forecast_current_default_location(runner, mock_api_calls, mock_display_functions, mock_config_file):
    mock_get_weather_data, mock_get_location_coordinates = mock_api_calls
    mock_current, mock_hourly, mock_daily, mock_chart, mock_error, mock_message = mock_display_functions

    # Simulate no default location set initially
    mock_config_file.write_text(json.dumps({"units": {}, "favorites": {}, "default_location": None}))

    # Mock user input for setting default location
    with patch('rich.prompt.Prompt.ask', side_effect=["yes", "Berlin"]):
        mock_get_location_coordinates.return_value = {"latitude": 52.52, "longitude": 13.41, "name": "Berlin"}
        mock_get_weather_data.return_value = {"current": {"temperature_2m": 10}, "timezone": "Europe/Berlin"}

        result = runner.invoke(cli, ["forecast"])

        assert result.exit_code == 0
        mock_message.assert_any_call("No data type specified (--current, --hourly, --daily). Defaulting to --current weather.")
        mock_message.assert_any_call("No location specified and no default location set.")
        mock_message.assert_any_call("Default location set to: Berlin (52.52, 13.41). This preference has been saved.")
        mock_current.assert_called_once()
        mock_get_weather_data.assert_called_once()

def test_forecast_current_with_location_name(runner, mock_api_calls, mock_display_functions):
    mock_get_weather_data, mock_get_location_coordinates = mock_api_calls
    mock_current, _, _, _, _, mock_message = mock_display_functions

    mock_get_location_coordinates.return_value = {"latitude": 34.05, "longitude": -118.25, "name": "Los Angeles"}
    mock_get_weather_data.return_value = {"current": {"temperature_2m": 20}, "timezone": "America/Los_Angeles"}

    result = runner.invoke(cli, ["forecast", "--location", "Los Angeles", "--current"])

    assert result.exit_code == 0
    mock_message.assert_any_call("Resolved location: Los Angeles (34.05, -118.25)")
    mock_current.assert_called_once()
    mock_get_location_coordinates.assert_called_once_with("Los Angeles")
    mock_get_weather_data.assert_called_once()

def test_forecast_hourly_with_lat_lon(runner, mock_api_calls, mock_display_functions):
    mock_get_weather_data, _ = mock_api_calls
    _, mock_hourly, _, _, _, _ = mock_display_functions

    mock_get_weather_data.return_value = {"hourly": {"temperature_2m": [10, 11]}, "timezone": "Europe/Berlin"}

    result = runner.invoke(cli, ["forecast", "--latitude", "52.52", "--longitude", "13.41", "--hourly", "temperature_2m"])

    assert result.exit_code == 0
    mock_hourly.assert_called_once()
    mock_get_weather_data.assert_called_once()

def test_forecast_daily_with_chart(runner, mock_api_calls, mock_display_functions):
    mock_get_weather_data, _ = mock_api_calls
    _, _, mock_daily, mock_chart, _, _ = mock_display_functions

    mock_get_weather_data.return_value = {
        "daily": {
            "time": ["2023-01-01"],
            "temperature_2m_max": [10.0],
            "temperature_2m_min": [0.0]
        },
        "timezone": "Europe/Berlin"
    }

    result = runner.invoke(cli, ["forecast", "--latitude", "52.52", "--longitude", "13.41", "--daily", "temperature_2m_max", "--daily", "temperature_2m_min", "--chart"])

    assert result.exit_code == 0
    mock_daily.assert_called_once()
    mock_chart.assert_called_once()
    mock_get_weather_data.assert_called_once()

def test_forecast_archive_with_dates(runner, mock_api_calls, mock_display_functions):
    mock_get_weather_data, _ = mock_api_calls
    _, _, mock_daily, _, _, _ = mock_display_functions

    mock_get_weather_data.return_value = {"daily": {"temperature_2m_max": [5]}, "timezone": "Europe/Berlin"}

    result = runner.invoke(cli, ["forecast", "--location", "Berlin", "--start-date", "2023-01-01", "--end-date", "2023-01-07", "--daily", "temperature_2m_max", "--archive"])

    assert result.exit_code == 0
    mock_daily.assert_called_once()
    mock_get_weather_data.assert_called_once()
    # Verify archive=True was passed to get_weather_data
    assert mock_get_weather_data.call_args[1]['archive'] is True

def test_forecast_invalid_lat_lon_input(runner, mock_display_functions):
    _, _, _, _, mock_error, _ = mock_display_functions
    result = runner.invoke(cli, ["forecast", "--latitude", "91.0", "--longitude", "13.41", "--current"])
    assert result.exit_code == 0 # Click handles validation, but our custom validation should trigger error display
    mock_error.assert_called_once_with("Invalid latitude or longitude. Latitude must be between -90 and 90, Longitude between -180 and 180.")

def test_forecast_api_error(runner, mock_api_calls, mock_display_functions):
    mock_get_weather_data, _ = mock_api_calls
    _, _, _, _, mock_error, _ = mock_display_functions

    mock_get_weather_data.return_value = {"error": "API is down"}

    result = runner.invoke(cli, ["forecast", "--location", "Test", "--current"])

    assert result.exit_code == 0
    mock_error.assert_called_once_with("API is down")

# --- Test config commands ---

def test_config_set_unit(runner, mock_display_functions, mock_config_file):
    _, _, _, _, _, mock_message = mock_display_functions
    result = runner.invoke(cli, ["config", "set-unit", "--temperature", "celsius"])
    assert result.exit_code == 0
    mock_message.assert_called_once_with("Default temperature unit set to: celsius. This preference has been saved.")
    config = json.loads(mock_config_file.read_text())
    assert config["units"]["temperature"] == "celsius"

def test_config_add_favorite(runner, mock_display_functions, mock_config_file):
    _, _, _, _, _, mock_message = mock_display_functions
    result = runner.invoke(cli, ["config", "add-favorite", "Home", "10.0", "20.0"])
    assert result.exit_code == 0
    mock_message.assert_called_once_with("Added favorite location: Home (10.0, 20.0). This preference has been saved.")
    config = json.loads(mock_config_file.read_text())
    assert config["favorites"]["Home"] == {"latitude": 10.0, "longitude": 20.0}

def test_config_list_favorites(runner, mock_display_functions, mock_config_file):
    mock_current, mock_hourly, mock_daily, mock_chart, mock_error, mock_message = mock_display_functions
    # Add some favorites first
    with open(mock_config_file, 'w') as f:
        json.dump({"units": {}, "favorites": {"Work": {"latitude": 30.0, "longitude": 40.0}}}, f)

    result = runner.invoke(cli, ["config", "list-favorites"])
    assert result.exit_code == 0
    # Assert that console.print was called with a rich.Table object containing expected content
    with patch('atmos_cli.main.console.print') as mock_console_print_main:
        result = runner.invoke(cli, ["config", "list-favorites"])
        assert result.exit_code == 0
        mock_console_print_main.assert_called_once()
        output_table = mock_console_print_main.call_args[0][0]
        assert isinstance(output_table, Table)
        assert "Work" in str(output_table)
        assert "30.0" in str(output_table)
        assert "40.0" in str(output_table)

def test_config_remove_favorite(runner, mock_display_functions, mock_config_file):
    _, _, _, _, _, mock_message = mock_display_functions
    # Add a favorite to remove
    with open(mock_config_file, 'w') as f:
        json.dump({"units": {}, "favorites": {"Home": {"latitude": 10.0, "longitude": 20.0}}}, f)

    result = runner.invoke(cli, ["config", "remove-favorite", "Home"])
    assert result.exit_code == 0
    mock_message.assert_called_once_with("Removed favorite location: Home. This preference has been updated.")
    config = json.loads(mock_config_file.read_text())
    assert "Home" not in config["favorites"]

def test_config_set_default_location_by_name(runner, mock_api_calls, mock_display_functions, mock_config_file):
    mock_get_weather_data, mock_get_location_coordinates = mock_api_calls
    _, _, _, _, _, mock_message = mock_display_functions

    mock_get_location_coordinates.return_value = {"latitude": 52.52, "longitude": 13.41, "name": "Berlin"}

    result = runner.invoke(cli, ["config", "set-default-location", "Berlin"])
    assert result.exit_code == 0
    mock_message.assert_called_once_with("Default location set to: Berlin (52.52, 13.41). This preference has been saved.")
    config = json.loads(mock_config_file.read_text())
    assert config["default_location"] == {"name": "Berlin", "latitude": 52.52, "longitude": 13.41}

# --- Test interactive command ---

def test_interactive_mode_exit(runner, mock_display_functions):
    _, _, _, _, _, mock_message = mock_display_functions
    # Simulate user typing 'exit'
    result = runner.invoke(cli, ["interactive"], input="exit\n")
    assert result.exit_code == 0
    mock_message.assert_any_call("Entering interactive mode. Type 'exit' or 'quit' to leave.")
    mock_message.assert_any_call("Exiting interactive mode.")

def test_interactive_mode_command_execution(runner, mock_api_calls, mock_display_functions):
    mock_get_weather_data, mock_get_location_coordinates = mock_api_calls
    mock_current, _, _, _, _, mock_message = mock_display_functions

    mock_get_location_coordinates.return_value = {"latitude": 34.05, "longitude": -118.25, "name": "Los Angeles"}
    mock_get_weather_data.return_value = {"current": {"temperature_2m": 20}, "timezone": "America/Los_Angeles"}

    # Simulate user typing a command and then 'exit'
    result = runner.invoke(cli, ["interactive"], input='forecast --location "Los Angeles" --current\nexit\n')

    assert result.exit_code == 0
    mock_message.assert_any_call("Resolved location: Los Angeles (34.05, -118.25)")
    mock_current.assert_called_once()
    mock_get_location_coordinates.assert_called_once_with("Los Angeles")
    mock_get_weather_data.assert_called_once()

# --- Test about command ---

def test_about_command(runner, mock_display_functions):
    _, _, _, _, _, _ = mock_display_functions # No specific message to mock, just check for Panel print
    with patch('atmos_cli.main.console.print') as mock_console_print:
        result = runner.invoke(cli, ["about"])
        assert result.exit_code == 0
        mock_console_print.assert_called_once()
        output_panel = mock_console_print.call_args[0][0]
        assert isinstance(output_panel, Panel)
        assert "Atmos CLI" in str(output_panel)
        assert "Version: 0.1.0" in str(output_panel)
