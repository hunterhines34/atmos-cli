import json
import os

CONFIG_FILE = os.path.expanduser("~/.atmos_cli_config.json")

def load_config() -> dict:
    """Loads configuration from the config file.

    Reads the JSON configuration file located at `~/.atmos_cli_config.json`.
    If the file does not exist or is corrupted, it returns a default configuration dictionary.

    Returns:
        dict: A dictionary containing the configuration settings.
            Structure:
            {
                "units": {"temperature": str, "wind_speed": str, "precipitation": str},
                "favorites": {name: {"latitude": float, "longitude": float}},
                "default_location": {"name": str, "latitude": float, "longitude": float} or None
            }
    """
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

def save_config(config: dict):
    """Saves configuration to the config file.

    Writes the provided configuration dictionary to `~/.atmos_cli_config.json` in JSON format.

    Args:
        config (dict): The configuration dictionary to save.
    """
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def get_unit_preference(unit_type: str) -> str:
    """Gets a specific unit preference.

    Retrieves the preferred unit for a given unit type (e.g., temperature) from the configuration.

    Args:
        unit_type (str): The type of unit to retrieve. One of 'temperature', 'wind_speed', or 'precipitation'.

    Returns:
        str: The preferred unit string (e.g., 'celsius', 'fahrenheit') or None if not found.
    """
    config = load_config()
    return config["units"].get(unit_type)

def set_unit_preference(unit_type: str, value: str):
    """Sets a specific unit preference.

    Updates the preferred unit for a given unit type and saves the configuration.

    Args:
        unit_type (str): The type of unit to set. One of 'temperature', 'wind_speed', or 'precipitation'.
        value (str): The value to set for the unit preference (e.g., 'celsius').
    """
    config = load_config()
    config["units"][unit_type] = value
    save_config(config)

def add_favorite_location(name: str, latitude: float, longitude: float):
    """Adds a favorite location.

    Saves a new favorite location with its coordinates to the configuration.

    Args:
        name (str): The name to assign to the favorite location.
        latitude (float): The latitude of the location.
        longitude (float): The longitude of the location.
    """
    config = load_config()
    config["favorites"][name] = {"latitude": latitude, "longitude": longitude}
    save_config(config)

def get_favorite_location(name: str) -> dict:
    """Gets a favorite location.

    Retrieves the coordinates for a saved favorite location by its name.

    Args:
        name (str): The name of the favorite location to retrieve.

    Returns:
        dict: A dictionary containing 'latitude' and 'longitude', or None if the location is not found.
    """
    config = load_config()
    return config["favorites"].get(name)

def list_favorite_locations() -> dict:
    """Lists all favorite locations.

    Retrieves all saved favorite locations from the configuration.

    Returns:
        dict: A dictionary where keys are location names and values are dictionaries containing coordinates.
    """
    config = load_config()
    return config["favorites"]

def remove_favorite_location(name: str) -> bool:
    """Removes a favorite location.

    Deletes a saved favorite location from the configuration by its name.

    Args:
        name (str): The name of the favorite location to remove.

    Returns:
        bool: True if the location was found and removed, False otherwise.
    """
    config = load_config()
    if name in config["favorites"]:
        del config["favorites"][name]
        save_config(config)
        return True
    return False

def get_default_location() -> dict:
    """Gets the default location.

    Retrieves the currently set default location from the configuration.

    Returns:
        dict: A dictionary containing 'name', 'latitude', and 'longitude' of the default location,
              or None if no default location is set.
    """
    config = load_config()
    return config.get("default_location")

def set_default_location(name: str, latitude: float, longitude: float):
    """Sets the default location.

    Updates the default location in the configuration. This location is used when no location
    is specified in CLI commands.

    Args:
        name (str): The name of the default location.
        latitude (float): The latitude of the default location.
        longitude (float): The longitude of the default location.
    """
    config = load_config()
    config["default_location"] = {"name": name, "latitude": latitude, "longitude": longitude}
    save_config(config)
