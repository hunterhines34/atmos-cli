import json
import os

CONFIG_FILE = os.path.expanduser("~/.atmos_cli_config.json")

def load_config():
    """Loads configuration from the config file."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
            # Ensure 'units', 'favorites', and 'default_location' keys exist
            if "units" not in config:
                config["units"] = {"temperature": "fahrenheit", "wind_speed": "mph", "precipitation": "inch"}
            if "favorites" not in config:
                config["favorites"] = {}
            if "default_location" not in config:
                config["default_location"] = None
            return config
        except json.JSONDecodeError:
            # If the file is empty or corrupted, return default config
            return {"units": {"temperature": "fahrenheit", "wind_speed": "mph", "precipitation": "inch"}, "favorites": {}, "default_location": None}
    # If file does not exist, return default config
    return {"units": {"temperature": "fahrenheit", "wind_speed": "mph", "precipitation": "inch"}, "favorites": {}, "default_location": None}

def save_config(config):
    """Saves configuration to the config file."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def get_unit_preference(unit_type: str):
    """Gets a specific unit preference."""
    config = load_config()
    return config["units"].get(unit_type)

def set_unit_preference(unit_type: str, value: str):
    """Sets a specific unit preference."""
    config = load_config()
    config["units"][unit_type] = value
    save_config(config)

def add_favorite_location(name: str, latitude: float, longitude: float):
    """Adds a favorite location."""
    config = load_config()
    config["favorites"][name] = {"latitude": latitude, "longitude": longitude}
    save_config(config)

def get_favorite_location(name: str):
    """Gets a favorite location."""
    config = load_config()
    return config["favorites"].get(name)

def list_favorite_locations():
    """Lists all favorite locations."""
    config = load_config()
    return config["favorites"]

def remove_favorite_location(name: str):
    """Removes a favorite location."""
    config = load_config()
    if name in config["favorites"]:
        del config["favorites"][name]
        save_config(config)
        return True
    return False

def get_default_location():
    """Gets the default location."""
    config = load_config()
    return config.get("default_location")

def set_default_location(name: str, latitude: float, longitude: float):
    """Sets the default location."""
    config = load_config()
    config["default_location"] = {"name": name, "latitude": latitude, "longitude": longitude}
    save_config(config)
