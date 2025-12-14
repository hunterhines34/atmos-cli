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


def test_negative_forecast_days_should_fail(runner, mock_api_calls):
    """Test that negative forecast_days value is rejected."""
    mock_get_weather_data, mock_get_location_coordinates = mock_api_calls

    mock_get_location_coordinates.return_value = {
        "latitude": 51.51,
        "longitude": -0.13,
        "name": "London"
    }

    mock_get_weather_data.return_value = {
        "timezone": "Europe/London",
        "current": {
            "time": "2023-11-15T12:00",
            "temperature_2m": 15
        },
        "current_units": {"temperature_2m": "°C"}
    }

    # This should fail because forecast_days is negative
    result = runner.invoke(cli, [
        "forecast",
        "--location", "London",
        "--current",
        "--forecast-days", "-1"
    ])

    # The command should fail with a validation error
    assert result.exit_code != 0
    assert "forecast" in result.output.lower() or "invalid" in result.output.lower()


def test_forecast_days_exceeds_maximum_should_fail(runner, mock_api_calls):
    """Test that forecast_days > 16 is rejected."""
    mock_get_weather_data, mock_get_location_coordinates = mock_api_calls

    mock_get_location_coordinates.return_value = {
        "latitude": 51.51,
        "longitude": -0.13,
        "name": "London"
    }

    # This should fail because forecast_days is > 16
    result = runner.invoke(cli, [
        "forecast",
        "--location", "London",
        "--current",
        "--forecast-days", "20"
    ])

    # The command should fail with a validation error
    assert result.exit_code != 0
    assert "forecast" in result.output.lower() or "invalid" in result.output.lower() or "16" in result.output


def test_negative_past_days_should_fail(runner, mock_api_calls):
    """Test that negative past_days value is rejected."""
    mock_get_weather_data, mock_get_location_coordinates = mock_api_calls

    mock_get_location_coordinates.return_value = {
        "latitude": 51.51,
        "longitude": -0.13,
        "name": "London"
    }

    # This should fail because past_days is negative
    result = runner.invoke(cli, [
        "forecast",
        "--location", "London",
        "--current",
        "--past-days", "-5"
    ])

    # The command should fail with a validation error
    assert result.exit_code != 0
    assert "past" in result.output.lower() or "invalid" in result.output.lower()


def test_past_days_exceeds_maximum_should_fail(runner, mock_api_calls):
    """Test that past_days > 92 is rejected."""
    mock_get_weather_data, mock_get_location_coordinates = mock_api_calls

    mock_get_location_coordinates.return_value = {
        "latitude": 51.51,
        "longitude": -0.13,
        "name": "London"
    }

    # This should fail because past_days is > 92
    result = runner.invoke(cli, [
        "forecast",
        "--location", "London",
        "--current",
        "--past-days", "100"
    ])

    # The command should fail with a validation error
    assert result.exit_code != 0
    assert "past" in result.output.lower() or "invalid" in result.output.lower() or "92" in result.output


def test_forecast_days_zero_should_fail(runner, mock_api_calls):
    """Test that forecast_days = 0 is rejected (minimum is 1)."""
    mock_get_weather_data, mock_get_location_coordinates = mock_api_calls

    mock_get_location_coordinates.return_value = {
        "latitude": 51.51,
        "longitude": -0.13,
        "name": "London"
    }

    # This should fail because forecast_days must be at least 1
    result = runner.invoke(cli, [
        "forecast",
        "--location", "London",
        "--current",
        "--forecast-days", "0"
    ])

    # The command should fail with a validation error
    assert result.exit_code != 0
    assert "forecast" in result.output.lower() or "invalid" in result.output.lower()


def test_valid_forecast_days_should_pass(runner, mock_api_calls):
    """Test that valid forecast_days value is accepted."""
    mock_get_weather_data, mock_get_location_coordinates = mock_api_calls

    mock_get_location_coordinates.return_value = {
        "latitude": 51.51,
        "longitude": -0.13,
        "name": "London"
    }

    mock_get_weather_data.return_value = {
        "timezone": "Europe/London",
        "current": {
            "time": "2023-11-15T12:00",
            "temperature_2m": 15
        },
        "current_units": {"temperature_2m": "°C"}
    }

    # This should succeed with valid forecast_days
    result = runner.invoke(cli, [
        "forecast",
        "--location", "London",
        "--current",
        "--forecast-days", "5"
    ])

    # The command should succeed
    assert result.exit_code == 0


def test_valid_past_days_should_pass(runner, mock_api_calls):
    """Test that valid past_days value is accepted."""
    mock_get_weather_data, mock_get_location_coordinates = mock_api_calls

    mock_get_location_coordinates.return_value = {
        "latitude": 51.51,
        "longitude": -0.13,
        "name": "London"
    }

    mock_get_weather_data.return_value = {
        "timezone": "Europe/London",
        "current": {
            "time": "2023-11-15T12:00",
            "temperature_2m": 15
        },
        "current_units": {"temperature_2m": "°C"}
    }

    # This should succeed with valid past_days
    result = runner.invoke(cli, [
        "forecast",
        "--location", "London",
        "--current",
        "--past-days", "7"
    ])

    # The command should succeed
    assert result.exit_code == 0
