# Atmos CLI

Atmos CLI is a powerful and intuitive command-line interface for fetching weather forecasts and historical data using the Open-Meteo API. Built with Python and the `rich` library, it provides a visually appealing and user-friendly experience with rich text, tables, and interactive features.

## Features

*   **Comprehensive Weather Data:** Access a wide range of weather variables including temperature, precipitation, wind speed, cloud cover, and more, for current, hourly, and daily forecasts.
*   **Flexible Location Input:** Specify locations using city names (e.g., "London"), city and state ("New York, NY"), city and country ("Paris, France"), or direct latitude/longitude coordinates.
*   **Default Location:** The application can detect and use a default location. If no location is specified and no default is set, it will prompt you to set one on the first run.
*   **Default to Current Weather:** If no specific data type (--current, --hourly, --daily) is requested, the application will automatically fetch and display current weather.
*   **Historical Data:** Retrieve past weather data for specified periods using date ranges or past days count.
*   **Enhanced Interactive Mode:** Engage in a continuous input loop, allowing you to run any `atmos` command directly within the interactive prompt, now with robust parsing for commands containing spaces or quotes, and command history (up/down arrow recall).
*   **Human-Readable Weather Codes:** Weather codes from the Open-Meteo API are now translated into clear, descriptive text for better understanding.
*   **Input Validation:** Latitude and longitude inputs are now validated to ensure they fall within valid geographical ranges.
*   **ASCII Art Temperature Chart:** Visualize daily minimum and maximum temperatures with a colorful, text-based bar chart directly in your terminal.
*   **Customizable Units:** Set your preferred units for temperature (Celsius/Fahrenheit), wind speed (km/h, m/s, mph, knots), and precipitation (mm/inch). Imperial units are set as default.
*   **Favorite Locations:** Save and manage your frequently used locations for quick access.
*   **Enhanced Configuration Feedback:** Clearer messages confirm when preferences like units and default locations are saved.
*   **About Command:** A new `atmos about` command provides quick information about the CLI.
*   **Full API Parameter Support:** All relevant parameters from the Open-Meteo Forecast and Archive APIs are exposed as command-line options.
*   **Rich CLI Experience:** Enjoy beautifully formatted output with `rich` tables, panels, and colors, enhancing readability and user experience.
*   **Modular Design:** Well-structured codebase for easy maintenance and extension.

## Installation

To install and set up Atmos CLI, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/hunterhines34/atmos-cli.git
    cd atmos-cli
    ```

2.  **Create and activate a virtual environment:**
    It's highly recommended to use a virtual environment to manage dependencies.
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
    On Windows, use:
    ```bash
    venv\Scripts\activate
    ```

3.  **Install the package in editable mode:**
    This will install the necessary dependencies and make the `atmos` command available in your activated virtual environment.
    ```bash
    python -m pip install -e .
    ```

## Usage

Atmos CLI uses `click` for its command-line interface. Once installed, you can simply use the `atmos` command.

### General Help

To see a list of all available commands and global options:

```bash
atmos --help
```

To get help for a specific command (e.g., `forecast`):

```bash
atmos forecast --help
```

### Basic Forecast

To get a basic weather forecast, you can now use a location name or latitude/longitude. If no location is specified, it will try to use your default location. If no data type (--current, --hourly, --daily) is specified, it defaults to showing current weather.

```bash
atmos forecast --location "London"
# This will now default to showing current weather for London
```

If it's your first run and no default location is set, the application will prompt you to set one.

### Forecast Options

*   `--latitude <float>`: Geographical WGS84 latitude (e.g., 34.05 for Los Angeles).
*   `--longitude <float>`: Geographical WGS84 longitude (e.g., -118.25 for Los Angeles).
*   `--location <string>`: City name, city and state, or city and country (e.g., "London", "New York, NY", "Paris, France"). This will use a geocoding service to find coordinates.
*   `--current`: Include current weather data in the output.
*   `--hourly <variable>`: Specify hourly weather variables to retrieve. Can be used multiple times (e.g., `--hourly temperature_2m --hourly wind_speed_10m`). See Open-Meteo API documentation for full list.
*   `--daily <variable>`: Specify daily weather variables to retrieve. Can be used multiple times (e.g., `--daily temperature_2m_max --daily precipitation_sum`). See Open-Meteo API documentation for full list.
*   `--temperature-unit <unit>`: Override the default temperature unit for this forecast (celsius or fahrenheit).
*   `--wind-speed-unit <unit>`: Override the default wind speed unit for this forecast (kmh, ms, mph, or kn).
*   `--precipitation-unit <unit>`: Override the default precipitation unit for this forecast (mm or inch).
*   `--timezone <timezone>`: Specify the timezone for the forecast (e.g., `America/New_York`). If not specified, the timezone is selected automatically for the given latitude and longitude.
*   `--forecast-days <int>`: Number of days to forecast (1-16). Defaults to 7 days. Cannot be used with `--start-date`/`--end-date`.
*   `--past-days <int>`: Number of past days to include for historical data (0-92). Defaults to 0. Cannot be used with `--start-date`/`--end-date`.
*   `--archive`: Fetch data from the historical archive API instead of the forecast API. Requires specifying `--past-days` or `--start-date`/`--end-date`.
*   `--favorite <name>`: Use a pre-saved favorite location by its name. Overrides `--latitude`, `--longitude`, and `--location`.
*   `--chart`: Display a daily temperature chart (ASCII art) if daily `temperature_2m_max` and `temperature_2m_min` data is available.
*   `--timeformat <format>`: Set the time format for the API response (`iso8601` or `unixtime`).
*   `--start-date <YYYY-MM-DD>`: Start date for historical data in YYYY-MM-DD format. Requires `--archive`. Cannot be used with `--forecast-days` or `--past-days`.
*   `--end-date <YYYY-MM-DD>`: End date for historical data in YYYY-MM-DD format. Requires `--archive`. Cannot be used with `--forecast-days` or `--past-days`.
*   `--models <model>`: Specify weather models to use. Can be used multiple times (e.g., `--models ecmwf_ifs --models gfs_seamless`). See Open-Meteo API documentation for full list of available models.
*   `--cell-selection <method>`: Method for selecting the geographical grid cell (`land`, `sea`, or `nearest`).
*   `--elevation <float>`: Elevation above sea level in meters. Defaults to the elevation of the location.
*   `--disable-stream`: Disable data streaming for faster response times. Only applicable to some API endpoints.

**Examples:**

*   **Current weather in Fahrenheit for New York City:**
    ```bash
    atmos forecast --location "New York, NY" --current --temperature-unit fahrenheit
    ```

*   **Hourly temperature and wind speed for the next 3 days:**
    ```bash
    atmos forecast --location "Los Angeles" --hourly temperature_2m --hourly wind_speed_10m --forecast-days 3
    ```

*   **Daily max/min temperature and precipitation sum for the past 7 days (archive data):**
    ```bash
    atmos forecast --location "Berlin" --daily temperature_2m_max --daily temperature_2m_min --daily precipitation_sum --past-days 7 --archive
    ```

*   **Using a favorite location:**
    ```bash
    atmos forecast --favorite "My Home" --current
    ```

*   **Displaying a daily temperature chart:**
    ```bash
    atmos forecast --location "London" --daily temperature_2m_max --daily temperature_2m_min --chart
    ```

*   **Historical data for a specific date range with a specific model:**
    ```bash
    atmos forecast --location "Berlin" --start-date 2023-01-01 --end-date 2023-01-07 --daily temperature_2m_max --archive --models ecmwf_ifs
    ```

### Configuration Management (`atmos config`)

The `config` command allows you to manage application preferences, including default units, favorite locations, and default location.

#### Set Default Units

You can set default units so you don't have to specify them with every `forecast` command. Imperial units are the default.

```bash
atmos config set-unit --temperature fahrenheit --wind-speed mph --precipitation inch
```

*   `--temperature <unit>`: Set the default temperature unit (`celsius`, `fahrenheit`).
*   `--wind-speed <unit>`: Set the default wind speed unit (`kmh`, `ms`, `mph`, `kn`).
*   `--precipitation <unit>`: Set the default precipitation unit (`mm`, `inch`).

#### Set Default Location

Set a default location that `atmos` will use if no location is specified in a `forecast` command.

```bash
atmos config set-default-location "London"
# Or using latitude,longitude
atmos config set-default-location "34.05,-118.25"
```

#### Add Favorite Location

Save a location with a friendly name for easy access.

```bash
atmos config add-favorite "Los Angeles" 34.05 -118.25
```

#### List Favorite Locations

View all your saved favorite locations.

```bash
atmos config list-favorites
```

#### Remove Favorite Location

Delete a saved favorite location.

```bash
atmos config remove-favorite "Los Angeles"
```

### Interactive Mode (`atmos interactive`)

Enter an interactive shell-like mode for continuous weather queries. In this mode, you can type any `atmos` command directly. Command history is supported, allowing you to recall previous commands with the up/down arrow keys.

```bash
atmos interactive
```

Example usage within interactive mode:

```
atmos> forecast --location "Paris" --current
atmos> config list-favorites
atmos> forecast --favorite "My Home" --daily temperature_2m_max
atmos> exit
```

Type `exit` or `quit` to leave the interactive mode.

### About Command (`atmos about`)

Display information about the Atmos CLI application, including its version and features.

```bash
atmos about
```

## Development

### Project Structure

```
atmos-cli/
├── venv/                   # Python virtual environment
├── atmos_cli/
│   ├── __init__.py         # Package initializer
│   ├── main.py             # Main CLI application logic (click commands)
│   ├── api.py              # Open-Meteo API interaction
│   ├── config.py           # Configuration management (units, favorites, default location)
│   ├── display.py          # Rich-based display functions for output
│   └── constants.py        # Stores API URLs, default values, and variable lists
├── pyproject.toml          # Project metadata and build configuration
├── README.md               # Project documentation
└── requirements.txt        # Python dependencies
```

### Open-Meteo API Details

The application leverages the free Open-Meteo API for weather data and the Open-Meteo Geocoding API for location resolution. You can find detailed API documentation at:

*   **Open-Meteo Weather API:** [https://open-meteo.com/en/docs](https://open-meteo.com/en/docs)
*   **Open-Meteo Geocoding API:** [https://open-meteo.com/en/docs/geocoding-api](https://open-meteo.com/en/docs/geocoding-api)

All relevant API parameters are exposed as command-line options in the `forecast` command.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is open-source and available under the [MIT License](https://opensource.org/licenses/MIT).