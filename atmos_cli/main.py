import click
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.table import Table # Added missing import
import sys
import shlex # Import shlex for robust command parsing
import readline # For command history
import atexit # To save history on exit
import os # For history file path

from atmos_cli.api import get_weather_data, get_location_coordinates
from atmos_cli.display import display_current_weather, display_hourly_weather, display_daily_weather, display_error, display_message, display_daily_temperature_chart
from atmos_cli.config import (
    load_config, save_config, set_unit_preference, get_unit_preference,
    add_favorite_location, get_favorite_location, list_favorite_locations,
    remove_favorite_location, get_default_location, set_default_location
)
from atmos_cli.constants import (
    DEFAULT_LATITUDE, DEFAULT_LONGITUDE, DEFAULT_TIMEZONE, DEFAULT_FORECAST_DAYS,
    DEFAULT_PAST_DAYS, TEMPERATURE_UNITS, WIND_SPEED_UNITS, PRECIPITATION_UNITS,
    HOURLY_WEATHER_VARIABLES, DAILY_WEATHER_VARIABLES, CURRENT_WEATHER_VARIABLES,
    TIME_FORMATS, WEATHER_MODELS, CELL_SELECTION_OPTIONS
)

console = Console()

# History file for interactive mode
HISTORY_FILE = os.path.expanduser("~/.atmos_cli_history")

def save_history():
    """Saves the readline history to a file.

    This function writes the current readline history to the file specified
    by `HISTORY_FILE` (usually `~/.atmos_cli_history`). It handles any
    exceptions that occur during the write process.
    """
    try:
        readline.write_history_file(HISTORY_FILE)
    except Exception as e:
        console.print(f"[bold red]Error saving history:[/bold red] {e}")

# Helper function for lat/lon validation
def validate_latitude(lat: float) -> bool:
    """Validates if the given latitude is within the valid range.

    Args:
        lat (float): The latitude value to check.

    Returns:
        bool: True if -90 <= lat <= 90, False otherwise.
    """
    return -90 <= lat <= 90

def validate_longitude(lon: float) -> bool:
    """Validates if the given longitude is within the valid range.

    Args:
        lon (float): The longitude value to check.

    Returns:
        bool: True if -180 <= lon <= 180, False otherwise.
    """
    return -180 <= lon <= 180

@click.group(help="\nA command-line weather application that fetches current, hourly, and daily weather data from the Open-Meteo API. It supports flexible location input, unit customization, favorite locations, and an interactive mode.\n")
def cli():
    """A command-line weather application.

    This is the main entry point for the Atmos CLI. It provides commands for fetching
    weather forecasts, managing configuration, and running in interactive mode.
    """
    pass

@cli.command(help="Fetch weather forecast or historical data for a specified location.\n\nExamples:\n  atmos forecast --location \"London\" --current\n  atmos forecast --latitude 34.05 --longitude -118.25 --hourly temperature_2m\n  atmos forecast --favorite \"My Home\" --daily temperature_2m_max --chart\n  atmos forecast --location \"Berlin\" --start-date 2023-01-01 --end-date 2023-01-07 --daily temperature_2m_max --archive --models ecmwf_ifs")
@click.option('--latitude', type=float, help='Geographical WGS84 latitude (e.g., 34.05 for Los Angeles).')
@click.option('--longitude', type=float, help='Geographical WGS84 longitude (e.g., -118.25 for Los Angeles).')
@click.option('--location', type=str, help='City name, city and state, or city and country (e.g., \"London\", \"New York, NY\", \"Paris, France\"). This will use a geocoding service to find coordinates.')
@click.option('--current', is_flag=True, help='Include current weather data in the output.')
@click.option('--hourly', multiple=True, type=click.Choice(HOURLY_WEATHER_VARIABLES), help='Specify hourly weather variables to retrieve. Can be used multiple times (e.g., --hourly temperature_2m --hourly wind_speed_10m). See Open-Meteo API documentation for full list.')
@click.option('--daily', multiple=True, type=click.Choice(DAILY_WEATHER_VARIABLES), help='Specify daily weather variables to retrieve. Can be used multiple times (e.g., --daily temperature_2m_max --daily precipitation_sum). See Open-Meteo API documentation for full list.')
@click.option('--temperature-unit', type=click.Choice(TEMPERATURE_UNITS), help='Override the default temperature unit for this forecast (celsius or fahrenheit).')
@click.option('--wind-speed-unit', type=click.Choice(WIND_SPEED_UNITS), help='Override the default wind speed unit for this forecast (kmh, ms, mph, or kn).')
@click.option('--precipitation-unit', type=click.Choice(PRECIPITATION_UNITS), help='Override the default precipitation unit for this forecast (mm or inch).')
@click.option('--timezone', type=str, help='Specify the timezone for the forecast (e.g., America/New_York). If not specified, the timezone is selected automatically for the given latitude and longitude.')
@click.option('--forecast-days', type=int, default=DEFAULT_FORECAST_DAYS, help='Number of days to forecast (1-16). Defaults to 7 days. Cannot be used with --start-date/--end-date.')
@click.option('--past-days', type=int, default=DEFAULT_PAST_DAYS, help='Number of past days to include for historical data (0-92). Defaults to 0. Cannot be used with --start-date/--end-date.')
@click.option('--archive', is_flag=True, help='Fetch data from the historical archive API instead of the forecast API. Requires specifying --past-days or --start-date/--end-date.')
@click.option('--favorite', type=str, help='Use a pre-saved favorite location by its name. Overrides --latitude, --longitude, and --location.')
@click.option('--chart', is_flag=True, help='Display a daily temperature chart (ASCII art) if daily temperature_2m_max and temperature_2m_min data is available.')
@click.option('--timeformat', type=click.Choice(TIME_FORMATS), help='Set the time format for the API response (iso8601 or unixtime).')
@click.option('--start-date', type=str, help='Start date for historical data in YYYY-MM-DD format. Requires --archive. Cannot be used with --forecast-days or --past-days.')
@click.option('--end-date', type=str, help='End date for historical data in YYYY-MM-DD format. Requires --archive. Cannot be used with --forecast-days or --past-days.')
@click.option('--models', multiple=True, type=click.Choice(WEATHER_MODELS), help='Specify weather models to use. Can be used multiple times. See Open-Meteo API documentation for full list.')
@click.option('--cell-selection', type=click.Choice(CELL_SELECTION_OPTIONS), help='Method for selecting the geographical grid cell (land, sea, or nearest).')
@click.option('--elevation', type=float, help='Elevation above sea level in meters. Defaults to the elevation of the location.')
@click.option('--disable-stream', is_flag=True, help='Disable data streaming for faster response times. Only applicable to some API endpoints.')
@click.pass_context
def forecast(
    ctx, latitude, longitude, location, current, hourly, daily, temperature_unit, wind_speed_unit,
    precipitation_unit, timezone, forecast_days, past_days, archive, favorite, chart,
    timeformat, start_date, end_date, models, cell_selection, elevation, disable_stream
):
    """Get weather forecast or historical data.

    Fetches and displays weather data based on the provided parameters.
    It handles location resolution (coordinates, city name, or favorites),
    fetches data from the Open-Meteo API, and displays it in a readable format.

    Args:
        latitude (float): Geographical WGS84 latitude.
        longitude (float): Geographical WGS84 longitude.
        location (str): City name or address to geocode.
        current (bool): Whether to fetch current weather data.
        hourly (tuple): List of hourly weather variables to fetch.
        daily (tuple): List of daily weather variables to fetch.
        temperature_unit (str): Unit for temperature (celsius, fahrenheit).
        wind_speed_unit (str): Unit for wind speed (kmh, ms, mph, kn).
        precipitation_unit (str): Unit for precipitation (mm, inch).
        timezone (str): Timezone for the forecast.
        forecast_days (int): Number of days to forecast.
        past_days (int): Number of past days for historical data.
        archive (bool): Whether to use the archive API.
        favorite (str): Name of a favorite location to use.
        chart (bool): Whether to display a daily temperature chart.
        timeformat (str): Time format (iso8601, unixtime).
        start_date (str): Start date for historical data (YYYY-MM-DD).
        end_date (str): End date for historical data (YYYY-MM-DD).
        models (tuple): List of weather models to use.
        cell_selection (str): Method for grid cell selection.
        elevation (float): Elevation in meters.
        disable_stream (bool): Whether to disable data streaming.
    """
    target_latitude = latitude
    target_longitude = longitude
    location_name = None

    # QoL: If no data type is specified, default to current weather
    if not (current or hourly or daily):
        current = True
        display_message("No data type specified (--current, --hourly, --daily). Defaulting to --current weather.")

    if favorite:
        fav_loc = get_favorite_location(favorite)
        if fav_loc:
            target_latitude = fav_loc["latitude"]
            target_longitude = fav_loc["longitude"]
            location_name = favorite
            display_message(f"Using favorite location: {favorite} ({target_latitude}, {target_longitude})")
        else:
            display_error(f"Favorite location '{favorite}' not found.")
            return
    elif location:
        coords = get_location_coordinates(location)
        if "error" in coords:
            display_error(coords["error"])
            return
        target_latitude = coords["latitude"]
        target_longitude = coords["longitude"]
        location_name = coords["name"]
        display_message(f"Resolved location: {location_name} ({target_latitude}, {target_longitude})")
    elif not (latitude or longitude):
        default_loc = get_default_location()
        if default_loc:
            target_latitude = default_loc["latitude"]
            target_longitude = default_loc["longitude"]
            location_name = default_loc["name"]
            display_message(f"Using default location: {location_name} ({target_latitude}, {target_longitude})")
        else:
            display_message("No location specified and no default location set.")
            response = Prompt.ask("[bold yellow]Would you like to set a default location now? (yes/no)[/bold yellow]", choices=["yes", "no"], default="yes")
            if response.lower() == "yes":
                loc_input = Prompt.ask("[bold cyan]Enter a city name, or latitude,longitude to set as default[/bold cyan]")
                if ',' in loc_input:
                    try:
                        lat_str, lon_str = loc_input.split(',')
                        lat, lon = float(lat_str.strip()), float(lon_str.strip())
                        if not validate_latitude(lat) or not validate_longitude(lon):
                            display_error("Invalid latitude or longitude. Latitude must be between -90 and 90, Longitude between -180 and 180.")
                            return
                        set_default_location(loc_input, lat, lon)
                        target_latitude = lat
                        target_longitude = lon
                        location_name = loc_input
                        display_message(f"Default location set to: {loc_input} ({lat}, {lon}). This preference has been saved.")
                    except ValueError:
                        display_error("Invalid latitude,longitude format. Please use: LATITUDE,LONGITUDE")
                        return
                else:
                    coords = get_location_coordinates(loc_input)
                    if "error" in coords:
                        display_error(coords["error"])
                        return
                    set_default_location(coords["name"], coords["latitude"], coords["longitude"])
                    target_latitude = coords["latitude"]
                    target_longitude = coords["longitude"]
                    location_name = coords["name"]
                    display_message(f"Default location set to: {location_name} ({target_latitude}, {target_longitude}). This preference has been saved.")
            else:
                display_error("Please specify a location using --latitude/--longitude, --location, or --favorite.")
                return

    if target_latitude is None or target_longitude is None:
        display_error("No valid location could be determined. Please provide one.")
        return

    if not validate_latitude(target_latitude) or not validate_longitude(target_longitude):
        display_error("Invalid latitude or longitude. Latitude must be between -90 and 90, Longitude between -180 and 180.")
        return

    # Validate forecast_days and past_days ranges (only if not using start_date/end_date)
    if not (start_date and end_date):
        if forecast_days < 1 or forecast_days > 16:
            ctx.fail("Invalid forecast_days value. Must be between 1 and 16.")
        if past_days < 0 or past_days > 92:
            ctx.fail("Invalid past_days value. Must be between 0 and 92.")

    params = {
        "latitude": target_latitude,
        "longitude": target_longitude,
    }

    # Only add timezone if explicitly provided by the user, otherwise default to auto
    if timezone:
        params["timezone"] = timezone
    else:
        params["timezone"] = "auto"

    # Handle date parameters: start_date/end_date take precedence over forecast_days/past_days
    if start_date and end_date:
        if forecast_days != DEFAULT_FORECAST_DAYS or past_days != DEFAULT_PAST_DAYS:
            display_error("Cannot use --start-date/--end-date with --forecast-days or --past-days. Please choose one method for date range specification.")
            return
        params["start_date"] = start_date
        params["end_date"] = end_date
        # If start_date/end_date are used, --archive is implicitly true
        archive = True
    else:
        params["forecast_days"] = forecast_days
        params["past_days"] = past_days

    # Apply unit preferences from config if not overridden by command-line options
    params["temperature_unit"] = temperature_unit or get_unit_preference("temperature")
    params["wind_speed_unit"] = wind_speed_unit or get_unit_preference("wind_speed")
    params["precipitation_unit"] = precipitation_unit or get_unit_preference("precipitation")

    if current:
        params["current"] = ",".join(CURRENT_WEATHER_VARIABLES)
    if hourly:
        params["hourly"] = ",".join(hourly)
    if daily:
        params["daily"] = ",".join(daily)

    # Add new API parameters
    if timeformat:
        params["timeformat"] = timeformat
    if models:
        params["models"] = ",".join(models)
    if cell_selection:
        params["cell_selection"] = cell_selection
    if elevation is not None:
        params["elevation"] = elevation
    if disable_stream:
        params["disable_stream"] = "true" # API expects "true" or "false" string

    with console.status("[bold green]Fetching weather data...[/bold green]") as status:
        data = get_weather_data(params, archive)

    if "error" in data:
        display_error(data["error"])
        return

    unit_system = "imperial" if params["temperature_unit"] == "fahrenheit" else "metric"

    if current:
        display_current_weather(data, unit_system)
    if hourly:
        display_hourly_weather(data, unit_system)
    if daily:
        display_daily_weather(data, unit_system)
        if chart:
            if "daily" in data and data["daily"] and "temperature_2m_max" in data["daily"] and "temperature_2m_min" in data["daily"]:
                display_daily_temperature_chart(data, unit_system)
            else:
                display_error("Daily temperature data (temperature_2m_max and temperature_2m_min) is required for charting. Please include these in your --daily options.")

@cli.command(help="Enter interactive mode for continuous weather queries. Type 'exit' or 'quit' to leave. Command history is supported (up/down arrow keys).")
def interactive():
    """Enter interactive mode for continuous weather queries.

    Starts a Read-Eval-Print Loop (REPL) where the user can enter `atmos` commands
    repeatedly without re-invoking the main script. Supports command history.
    """
    display_message("Entering interactive mode. Type 'exit' or 'quit' to leave.")

    # Load history if available
    if os.path.exists(HISTORY_FILE):
        try:
            readline.read_history_file(HISTORY_FILE)
        except Exception as e:
            console.print(f"[bold red]Error loading history:[/bold red] {e}")
    atexit.register(save_history)

    while True:
        try:
            # Use input() for readline support
            command_line = input(str(console.render_str("[bold cyan]atmos>[/bold cyan]")) + " ").strip()

            if command_line.lower() in ["exit", "quit"]:
                display_message("Exiting interactive mode.")
                break

            if not command_line:
                continue

            # Use shlex.split for robust parsing of command line arguments
            args = shlex.split(command_line)

            # Prepend 'atmos' to the arguments to simulate a full command
            full_args = ["atmos"] + args

            # Create a new context and invoke the CLI with the parsed arguments
            # Temporarily redirect sys.argv to simulate the command line input
            old_argv = sys.argv
            sys.argv = full_args
            try:
                # Invoke the main CLI command. This will parse and execute the command.
                # We pass standalone_mode=False to prevent click from exiting the program.
                cli.main(args=full_args[1:], standalone_mode=False)
            finally:
                sys.argv = old_argv # Restore sys.argv

        except EOFError: # Ctrl+D
            display_message("Exiting interactive mode.")
            break
        except KeyboardInterrupt: # Ctrl+C
            console.print("\n[bold yellow]Operation cancelled.[/bold yellow]")
            continue
        except Exception as e:
            display_error(f"An error occurred in interactive mode: {e}")

@cli.group(help="Manage application configuration and preferences, including default units, favorite locations, and default location.")
def config():
    """Manage application configuration and preferences.

    Provides subcommands to set units, manage favorite locations, and set a default location.
    """
    pass

@config.command(name="set-unit", help="Set default units for temperature, wind speed, and precipitation.\n\nExample: atmos config set-unit --temperature fahrenheit --wind-speed mph")
@click.option('--temperature', type=click.Choice(TEMPERATURE_UNITS), help='Set the default temperature unit (celsius or fahrenheit).')
@click.option('--wind-speed', type=click.Choice(WIND_SPEED_UNITS), help='Set the default wind speed unit (kmh, ms, mph, or kn).')
@click.option('--precipitation', type=click.Choice(PRECIPITATION_UNITS), help='Set the default precipitation unit (mm or inch).')
def set_unit(temperature, wind_speed, precipitation):
    """Set default units for weather data.

    Updates the configuration file with the specified unit preferences.

    Args:
        temperature (str): Default temperature unit.
        wind_speed (str): Default wind speed unit.
        precipitation (str): Default precipitation unit.
    """
    if temperature:
        set_unit_preference("temperature", temperature)
        display_message(f"Default temperature unit set to: {temperature}. This preference has been saved.")
    if wind_speed:
        set_unit_preference("wind_speed", wind_speed)
        display_message(f"Default wind speed unit set to: {wind_speed}. This preference has been saved.")
    if precipitation:
        set_unit_preference("precipitation", precipitation)
        display_message(f"Default precipitation unit set to: {precipitation}. This preference has been saved.")
    if not (temperature or wind_speed or precipitation):
        display_message("No unit specified to set. Use --temperature, --wind-speed, or --precipitation.")

@config.command(name="add-favorite", help="Add a favorite location with a given name, latitude, and longitude.\n\nExample: atmos config add-favorite \"Los Angeles\" 34.05 -118.25")
@click.argument('name', type=str)
@click.argument('latitude', type=float)
@click.argument('longitude', type=float)
def add_favorite(name, latitude, longitude):
    """Add a favorite location.

    Saves a new location to the favorites list in the configuration.

    Args:
        name (str): Name of the location.
        latitude (float): Latitude of the location.
        longitude (float): Longitude of the location.
    """
    if not validate_latitude(latitude) or not validate_longitude(longitude):
        display_error("Invalid latitude or longitude. Latitude must be between -90 and 90, Longitude between -180 and 180.")
        return
    add_favorite_location(name, latitude, longitude)
    display_message(f"Added favorite location: {name} ({latitude}, {longitude}). This preference has been saved.")

@config.command(name="list-favorites", help="List all saved favorite locations.")
def list_favorites():
    """List all saved favorite locations.

    Displays a table of all favorite locations stored in the configuration.
    """
    favorites = list_favorite_locations()
    if favorites:
        table = Table(title="[bold blue]Favorite Locations[/bold blue]", show_header=True, header_style="bold magenta")
        table.add_column("Name", style="cyan")
        table.add_column("Latitude", style="green")
        table.add_column("Longitude", style="green")
        for name, loc in favorites.items():
            table.add_row(name, str(loc["latitude"]), str(loc["longitude"]))
        console.print(table)
    else:
        display_message("No favorite locations saved.")

@config.command(name="remove-favorite", help="Remove a saved favorite location by its name.\n\nExample: atmos config remove-favorite \"Los Angeles\"")
@click.argument('name', type=str)
def remove_favorite(name):
    """Remove a favorite location.

    Deletes a location from the favorites list in the configuration.

    Args:
        name (str): The name of the favorite location to remove.
    """
    if remove_favorite_location(name):
        display_message(f"Removed favorite location: {name}. This preference has been updated.")
    else:
        display_error(f"Favorite location '{name}' not found.")

@config.command(name="set-default-location", help="Set a default location using a city name or latitude,longitude. This location will be used if no location is specified in a forecast command.\n\nExample: atmos config set-default-location \"London\"\nExample: atmos config set-default-location \"34.05,-118.25\"")
@click.argument('location_input', type=str)
def set_default_location_cmd(location_input):
    """Set a default location using a city name or latitude,longitude.

    Updates the default location in the configuration.

    Args:
        location_input (str): The location to set as default. Can be a city name
                              or a coordinate string "lat,lon".
    """
    if ',' in location_input:
        try:
            lat_str, lon_str = location_input.split(',')
            lat, lon = float(lat_str.strip()), float(lon_str.strip())
            if not validate_latitude(lat) or not validate_longitude(lon):
                display_error("Invalid latitude or longitude. Latitude must be between -90 and 90, Longitude between -180 and 180.")
                return
            set_default_location(location_input, lat, lon)
            display_message(f"Default location set to: {location_input} ({lat}, {lon}). This preference has been saved.")
        except ValueError:
            display_error("Invalid latitude,longitude format. Please use: LATITUDE,LONGITUDE")
    else:
        coords = get_location_coordinates(location_input)
        if "error" in coords:
            display_error(coords["error"])
            return
        set_default_location(coords["name"], coords["latitude"], coords["longitude"])
        display_message(f"Default location set to: {coords['name']} ({coords['latitude']}, {coords['longitude']}). This preference has been saved.")

@cli.command(help="Display information about the Atmos CLI application.")
def about():
    """Display information about the Atmos CLI application.

    Shows version, author, description, and features.
    """
    console.print(Panel(
        "[bold blue]Atmos CLI[/bold blue]\n\n" +
        "Version: 0.1.0\n" +
        "Author: Hunter\n" +
        "Description: A command-line weather application using the Open-Meteo API.\n" +
        "Features: Current, hourly, and daily forecasts, flexible location input, default location, favorite locations, customizable units, interactive mode with history, human-readable weather codes, input validation, and ASCII art temperature charts.\n\n" +
        "For more information, visit the project's GitHub repository (if applicable)."
    , title="[bold green]About Atmos CLI[/bold green]"))

if __name__ == '__main__':
    cli()
