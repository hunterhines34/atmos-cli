import pytest
from click.testing import CliRunner
from unittest.mock import patch
from atmos_cli.main import cli
import datetime

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

def test_chart_unixtime_display(runner, mock_api_calls):
    mock_get_weather_data, mock_get_location_coordinates = mock_api_calls

    mock_get_location_coordinates.return_value = {"latitude": 52.52, "longitude": 13.41, "name": "Berlin"}

    timestamp = 1700000000
    expected_date = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')

    # Mock response with unixtime (integers)
    mock_get_weather_data.return_value = {
        "timezone": "Europe/Berlin",
        "daily": {
            "time": [timestamp],
            "temperature_2m_max": [15],
            "temperature_2m_min": [5]
        },
        "daily_units": {"temperature_2m_max": "°C"}
    }

    # Test daily chart with unixtime
    result = runner.invoke(cli, ["forecast", "--location", "Berlin", "--daily", "temperature_2m_max", "--daily", "temperature_2m_min", "--chart", "--timeformat", "unixtime"])

    assert result.exit_code == 0

    # After the fix, the timestamp should NOT appear in the output (except maybe if debugging, but here it shouldn't)
    assert str(timestamp) not in result.output

    # And we can check that the formatted date IS in the output
    assert expected_date in result.output
