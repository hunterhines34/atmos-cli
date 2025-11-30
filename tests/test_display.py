import pytest
from unittest.mock import MagicMock, patch
from io import StringIO

from atmos_cli.display import (
    display_current_weather,
    display_hourly_weather,
    display_daily_weather,
    display_daily_temperature_chart,
    display_error,
    display_message,
    get_weather_description
)
from atmos_cli.constants import WEATHER_CODES

# Mock data for display tests
MOCK_WEATHER_DATA_FULL = {
    "latitude": 52.52,
    "longitude": 13.41,
    "timezone": "Europe/Berlin",
    "current_units": {"time": "iso8601", "temperature_2m": "°F", "precipitation": "inch", "wind_speed_10m": "mp/h"},
    "current": {
        "time": "2023-10-27T10:00",
        "temperature_2m": 55.0,
        "apparent_temperature": 53.0,
        "is_day": 1,
        "precipitation": 0.0,
        "rain": 0.0,
        "showers": 0.0,
        "snowfall": 0.0,
        "weather_code": 3,
        "cloud_cover": 100,
        "wind_speed_10m": 10.0,
        "wind_direction_10m": 270,
        "wind_gusts_10m": 15.0
    },
    "hourly_units": {"time": "iso8601", "temperature_2m": "°F", "apparent_temperature": "°F", "precipitation": "inch", "wind_speed_10m": "mp/h", "cloud_cover": "%"},
    "hourly": {
        "time": ["2023-10-27T10:00", "2023-10-27T11:00"],
        "temperature_2m": [55.0, 56.0],
        "apparent_temperature": [53.0, 54.0],
        "precipitation": [0.0, 0.1],
        "wind_speed_10m": [10.0, 12.0],
        "cloud_cover": [100, 90],
        "weather_code": [3, 61]
    },
    "daily_units": {"time": "iso8601", "temperature_2m_max": "°F", "temperature_2m_min": "°F", "precipitation_sum": "inch", "wind_speed_10m_max": "mp/h"},
    "daily": {
        "time": ["2023-10-27", "2023-10-28"],
        "temperature_2m_max": [60.0, 58.0],
        "temperature_2m_min": [50.0, 48.0],
        "precipitation_sum": [0.0, 0.5],
        "wind_speed_10m_max": [15.0, 12.0],
        "weather_code": [3, 63]
    }
}

MOCK_WEATHER_DATA_EMPTY = {
    "latitude": 0.0,
    "longitude": 0.0,
    "timezone": "Etc/GMT",
    "current_units": {},
    "current": {},
    "hourly_units": {},
    "hourly": {},
    "daily_units": {}
}

def test_get_weather_description():
    assert get_weather_description(0) == "Clear sky"
    assert get_weather_description(61) == "Rain: Slight"
    assert get_weather_description(999) == "Unknown code: 999"

def test_display_current_weather_success(capsys):
    display_current_weather(MOCK_WEATHER_DATA_FULL)
    captured = capsys.readouterr()
    output = captured.out
    assert "Current Weather in Europe/Berlin" in output
    assert "Temperature" in output
    assert "55.0 °F" in output
    assert "Weather" in output
    assert "Overcast" in output

def test_display_current_weather_error(capsys):
    display_current_weather({"error": "API failed"})
    captured = capsys.readouterr()
    output = captured.out
    assert "Error: API failed" in output

def test_display_current_weather_no_data(capsys):
    display_current_weather(MOCK_WEATHER_DATA_EMPTY)
    captured = capsys.readouterr()
    output = captured.out
    assert "No current weather data available." in output

def test_display_hourly_weather_success(capsys):
    display_hourly_weather(MOCK_WEATHER_DATA_FULL)
    captured = capsys.readouterr()
    output = captured.out
    assert "Hourly Weather in Europe/Berlin" in output
    assert "Temp °F" in output
    assert "55.0" in output
    assert "Overcast" in output
    # Check for parts of the string because rich table might wrap text
    assert "Rain:" in output
    assert "Slight" in output

def test_display_hourly_weather_error(capsys):
    display_hourly_weather({"error": "API failed"})
    captured = capsys.readouterr()
    output = captured.out
    assert "Error: API failed" in output

def test_display_hourly_weather_no_data(capsys):
    display_hourly_weather(MOCK_WEATHER_DATA_EMPTY)
    captured = capsys.readouterr()
    output = captured.out
    assert "No hourly weather data available." in output

def test_display_daily_weather_success(capsys):
    display_daily_weather(MOCK_WEATHER_DATA_FULL)
    captured = capsys.readouterr()
    output = captured.out
    assert "Daily Weather in Europe/Berlin" in output
    assert "Max Temp" in output
    assert "°F" in output
    assert "60.0" in output
    assert "Overcast" in output
    # Check for parts of the string because rich table might wrap text
    assert "Rain:" in output
    assert "Moderate" in output

def test_display_daily_weather_error(capsys):
    display_daily_weather({"error": "API failed"})
    captured = capsys.readouterr()
    output = captured.out
    assert "Error: API failed" in output

def test_display_daily_weather_no_data(capsys):
    display_daily_weather(MOCK_WEATHER_DATA_EMPTY)
    captured = capsys.readouterr()
    output = captured.out
    assert "No daily weather data available." in output

def test_display_daily_temperature_chart_success(capsys):
    display_daily_temperature_chart(MOCK_WEATHER_DATA_FULL)
    captured = capsys.readouterr()
    output = captured.out
    assert "Daily Temperature Chart in Europe/Berlin (°F)" in output
    assert "█" in output # Check for chart characters
    assert "50.0 - 60.0 °F" in output

def test_display_daily_temperature_chart_no_data(capsys):
    display_daily_temperature_chart(MOCK_WEATHER_DATA_EMPTY)
    captured = capsys.readouterr()
    output = captured.out
    assert "Not enough daily temperature data for charting." in output

def test_display_error(capsys):
    display_error("Something went wrong!")
    captured = capsys.readouterr()
    output = captured.out
    assert "Error: Something went wrong!" in output

def test_display_message(capsys):
    display_message("Operation successful.")
    captured = capsys.readouterr()
    output = captured.out
    assert "Info: Operation successful." in output