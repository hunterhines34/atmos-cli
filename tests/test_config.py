import pytest
import json
import os
from atmos_cli.config import (
    load_config, save_config, set_unit_preference, get_unit_preference,
    add_favorite_location, get_favorite_location, list_favorite_locations,
    remove_favorite_location, get_default_location, set_default_location
)

# Fixture to create a temporary config file for each test
@pytest.fixture
def temp_config_file(tmp_path):
    config_path = tmp_path / ".atmos_cli_config.json"
    # Patch the CONFIG_FILE constant to point to our temporary file
    original_config_file = os.path.expanduser("~/.atmos_cli_config.json")
    os.environ["ATMOS_CLI_CONFIG_FILE"] = str(config_path) # Use an env var to pass the path

    # Ensure the config module uses the patched path
    import atmos_cli.config
    atmos_cli.config.CONFIG_FILE = config_path

    yield config_path

    # Clean up after test
    if os.path.exists(config_path):
        os.remove(config_path)
    del os.environ["ATMOS_CLI_CONFIG_FILE"]
    atmos_cli.config.CONFIG_FILE = original_config_file # Restore original path


def test_load_config_no_file(temp_config_file):
    config = load_config()
    assert config == {"units": {"temperature": "fahrenheit", "wind_speed": "mph", "precipitation": "inch"}, "favorites": {}, "default_location": None}

def test_load_config_empty_file(temp_config_file):
    temp_config_file.write_text("")
    config = load_config()
    assert config == {"units": {"temperature": "fahrenheit", "wind_speed": "mph", "precipitation": "inch"}, "favorites": {}, "default_location": None}

def test_load_config_malformed_json(temp_config_file):
    temp_config_file.write_text("{\"units\": {""}") # Malformed JSON
    config = load_config()
    assert config == {"units": {"temperature": "fahrenheit", "wind_speed": "mph", "precipitation": "inch"}, "favorites": {}, "default_location": None}

def test_load_config_valid_file(temp_config_file):
    test_data = {"units": {"temperature": "celsius"}, "favorites": {"home": {"latitude": 10.0, "longitude": 20.0}}, "default_location": {"name": "Test", "latitude": 1.0, "longitude": 2.0}}
    temp_config_file.write_text(json.dumps(test_data))
    config = load_config()
    assert config == test_data

def test_load_config_missing_keys(temp_config_file):
    test_data = {"units": {"temperature": "celsius"}}
    temp_config_file.write_text(json.dumps(test_data))
    config = load_config()
    assert "favorites" in config
    assert "default_location" in config
    assert config["favorites"] == {}
    assert config["default_location"] is None

def test_save_config(temp_config_file):
    config_data = {"units": {"temperature": "celsius"}, "favorites": {}}
    save_config(config_data)
    loaded_data = json.loads(temp_config_file.read_text())
    assert loaded_data["units"]["temperature"] == "celsius"

def test_get_unit_preference(temp_config_file):
    set_unit_preference("temperature", "celsius")
    assert get_unit_preference("temperature") == "celsius"

def test_set_unit_preference(temp_config_file):
    set_unit_preference("temperature", "fahrenheit")
    config = load_config()
    assert config["units"]["temperature"] == "fahrenheit"

def test_add_favorite_location(temp_config_file):
    add_favorite_location("work", 30.0, 40.0)
    config = load_config()
    assert config["favorites"]["work"] == {"latitude": 30.0, "longitude": 40.0}

def test_get_favorite_location(temp_config_file):
    add_favorite_location("work", 30.0, 40.0)
    fav = get_favorite_location("work")
    assert fav == {"latitude": 30.0, "longitude": 40.0}
    assert get_favorite_location("nonexistent") is None

def test_list_favorite_locations(temp_config_file):
    add_favorite_location("work", 30.0, 40.0)
    add_favorite_location("home", 10.0, 20.0)
    favorites = list_favorite_locations()
    assert "work" in favorites
    assert "home" in favorites

def test_remove_favorite_location(temp_config_file):
    add_favorite_location("work", 30.0, 40.0)
    assert remove_favorite_location("work") is True
    config = load_config()
    assert "work" not in config["favorites"]
    assert remove_favorite_location("nonexistent") is False

def test_get_default_location(temp_config_file):
    assert get_default_location() is None
    set_default_location("Test Loc", 1.0, 2.0)
    default_loc = get_default_location()
    assert default_loc == {"name": "Test Loc", "latitude": 1.0, "longitude": 2.0}

def test_set_default_location(temp_config_file):
    set_default_location("New Default", 5.0, 6.0)
    config = load_config()
    assert config["default_location"] == {"name": "New Default", "latitude": 5.0, "longitude": 6.0}
