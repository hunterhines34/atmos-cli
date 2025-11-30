from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
from atmos_cli.constants import WEATHER_CODES

console = Console()

def get_weather_description(code: int) -> str:
    """Returns a human-readable description for a WMO weather code.

    Args:
        code (int): The WMO weather code returned by the API.

    Returns:
        str: A descriptive string corresponding to the weather code.
             Returns "Unknown code: {code}" if the code is not found.
    """
    return WEATHER_CODES.get(code, f"Unknown code: {code}")

def display_current_weather(data: dict, unit_system: str = "imperial"):
    """Displays current weather data using rich.

    Formatted as a table with relevant weather metrics.

    Args:
        data (dict): The weather data dictionary returned by the API.
            Expected to contain 'current', 'current_units', and 'timezone'.
        unit_system (str): The unit system to use for display ('imperial' or 'metric').
            Currently used for internal logic if needed, though units are largely derived from API response.
            Defaults to "imperial".
    """
    if "error" in data:
        console.print(Panel(f"[bold red]Error:[/bold red] {data['error']}", title="[bold red]Weather Data Error[/bold red]"))
        return

    current = data.get("current", {})
    current_units = data.get("current_units", {})
    timezone = data.get("timezone", "N/A") # Get timezone from API response

    if not current:
        console.print(Panel("[bold yellow]No current weather data available.[/bold yellow]", title="[bold yellow]Current Weather[/bold yellow]"))
        return

    table = Table(title=f"[bold blue]Current Weather in {timezone}[/bold blue]", show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")

    temp_unit = current_units.get("temperature_2m", "°C")
    wind_unit = current_units.get("wind_speed_10m", "m/s")
    precip_unit = current_units.get("precipitation", "mm")

    weather_code = current.get("weather_code")
    weather_description = get_weather_description(weather_code) if weather_code is not None else "N/A"

    table.add_row("Time", Text(current.get("time", "N/A")))
    table.add_row("Temperature", f"{current.get('temperature_2m', 'N/A')} {temp_unit}")
    table.add_row("Apparent Temperature", f"{current.get('apparent_temperature', 'N/A')} {temp_unit}")
    table.add_row("Is Day", "Yes" if current.get("is_day") == 1 else "No")
    table.add_row("Precipitation", f"{current.get('precipitation', 'N/A')} {precip_unit}")
    table.add_row("Rain", f"{current.get('rain', 'N/A')} {precip_unit}")
    table.add_row("Showers", f"{current.get('showers', 'N/A')} {precip_unit}")
    table.add_row("Snowfall", f"{current.get('snowfall', 'N/A')} {precip_unit}")
    table.add_row("Weather", weather_description)
    table.add_row("Cloud Cover", f"{current.get('cloud_cover', 'N/A')}%")
    table.add_row("Wind Speed", f"{current.get('wind_speed_10m', 'N/A')} {wind_unit}")
    table.add_row("Wind Direction", f"{current.get('wind_direction_10m', 'N/A')}°")
    table.add_row("Wind Gusts", f"{current.get('wind_gusts_10m', 'N/A')} {wind_unit}")

    console.print(table)

def display_hourly_weather(data: dict, unit_system: str = "imperial"):
    """Displays hourly weather data using rich.

    Formatted as a table with time as the first column and selected metrics as subsequent columns.

    Args:
        data (dict): The weather data dictionary returned by the API.
            Expected to contain 'hourly', 'hourly_units', and 'timezone'.
        unit_system (str): The unit system to use for display ('imperial' or 'metric').
            Defaults to "imperial".
    """
    if "error" in data:
        console.print(Panel(f"[bold red]Error:[/bold red] {data['error']}", title="[bold red]Weather Data Error[/bold red]"))
        return

    hourly = data.get("hourly", {})
    hourly_units = data.get("hourly_units", {})
    timezone = data.get("timezone", "N/A") # Get timezone from API response

    if not hourly or not hourly.get("time"):
        console.print(Panel("[bold yellow]No hourly weather data available.[/bold yellow]", title="[bold yellow]Hourly Weather[/bold yellow]"))
        return

    table = Table(title=f"[bold blue]Hourly Weather in {timezone}[/bold blue]", show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("Time", style="cyan", no_wrap=True)

    # Define a mapping from API key to display name and unit key
    display_map = {
        "temperature_2m": {"name": "Temp", "unit_key": "temperature_2m", "style": "green"},
        "apparent_temperature": {"name": "Feels Like", "unit_key": "apparent_temperature", "style": "green"},
        "precipitation": {"name": "Precip", "unit_key": "precipitation", "style": "blue"},
        "wind_speed_10m": {"name": "Wind", "unit_key": "wind_speed_10m", "style": "yellow"},
        "cloud_cover": {"name": "Cloud Cover", "unit_key": "cloud_cover", "style": "white"},
        "weather_code": {"name": "Weather", "unit_key": None, "style": "magenta"},
    }

    columns_to_display = []
    for api_key, info in display_map.items():
        if api_key in hourly:
            columns_to_display.append(api_key)
            unit = hourly_units.get(info["unit_key"], "") if info["unit_key"] else ""
            table.add_column(f"{info['name']} {unit}".strip(), style=info["style"])

    for i, time_val in enumerate(hourly["time"]):
        row_values = [Text(time_val.split('T')[1])]
        for api_key in columns_to_display:
            value = hourly[api_key][i]
            if api_key == "weather_code":
                row_values.append(get_weather_description(value))
            elif api_key == "cloud_cover":
                row_values.append(f"{value}%")
            else:
                row_values.append(str(value))
        table.add_row(*row_values)

    console.print(table)

def display_daily_weather(data: dict, unit_system: str = "imperial"):
    """Displays daily weather data using rich.

    Formatted as a table with date as the first column and selected metrics as subsequent columns.

    Args:
        data (dict): The weather data dictionary returned by the API.
            Expected to contain 'daily', 'daily_units', and 'timezone'.
        unit_system (str): The unit system to use for display ('imperial' or 'metric').
            Defaults to "imperial".
    """
    if "error" in data:
        console.print(Panel(f"[bold red]Error:[/bold red] {data['error']}", title="[bold red]Weather Data Error[/bold red]"))
        return

    daily = data.get("daily", {})
    daily_units = data.get("daily_units", {})
    timezone = data.get("timezone", "N/A") # Get timezone from API response

    if not daily or not daily.get("time"):
        console.print(Panel("[bold yellow]No daily weather data available.[/bold yellow]", title="[bold yellow]Daily Weather[/bold yellow]"))
        return

    table = Table(title=f"[bold blue]Daily Weather in {timezone}[/bold blue]", show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("Date", style="cyan", no_wrap=True)

    # Define a mapping from API key to display name and unit key
    display_map = {
        "temperature_2m_max": {"name": "Max Temp", "unit_key": "temperature_2m_max", "style": "red"},
        "temperature_2m_min": {"name": "Min Temp", "unit_key": "temperature_2m_min", "style": "blue"},
        "precipitation_sum": {"name": "Precip Sum", "unit_key": "precipitation_sum", "style": "green"},
        "wind_speed_10m_max": {"name": "Wind Max", "unit_key": "wind_speed_10m_max", "style": "yellow"},
        "weather_code": {"name": "Weather", "unit_key": None, "style": "magenta"}, # Weather code has no unit
    }

    # Add columns dynamically based on what's available in 'daily' data
    columns_to_display = []
    for api_key, info in display_map.items():
        if api_key in daily:
            columns_to_display.append(api_key)
            unit = daily_units.get(info["unit_key"], "") if info["unit_key"] else ""
            table.add_column(f"{info['name']} {unit}".strip(), style=info["style"])

    for i, time_val in enumerate(daily["time"]):
        row_values = [Text(time_val)]
        for api_key in columns_to_display:
            value = daily[api_key][i]
            if api_key == "weather_code":
                row_values.append(get_weather_description(value))
            else:
                row_values.append(str(value))
        table.add_row(*row_values)

    console.print(table)

def display_daily_temperature_chart(data: dict, unit_system: str = "imperial"):
    """Displays a daily temperature chart using ASCII art with rich.

    Visualizes the temperature range (min to max) for each day.

    Args:
        data (dict): The weather data dictionary returned by the API.
            Expected to contain 'daily', 'daily_units', and 'timezone'.
            Requires 'temperature_2m_max' and 'temperature_2m_min' in 'daily'.
        unit_system (str): The unit system to use for display ('imperial' or 'metric').
            Defaults to "imperial".
    """
    daily = data.get("daily", {})
    daily_units = data.get("daily_units", {})
    timezone = data.get("timezone", "N/A") # Get timezone from API response

    if not daily or not daily.get("time") or not daily.get("temperature_2m_max") or not daily.get("temperature_2m_min"):
        console.print(Panel("[bold yellow]Not enough daily temperature data for charting. Requires 'temperature_2m_max' and 'temperature_2m_min'.[/bold yellow]", title="[bold yellow]Chart Error[/bold yellow]"))
        return

    times = daily["time"]
    max_temps = daily["temperature_2m_max"]
    min_temps = daily["temperature_2m_min"]
    temp_unit = daily_units.get("temperature_2m_max", "°C")

    all_temps = max_temps + min_temps
    min_val = min(all_temps)
    max_val = max(all_temps)

    # Adjust range to ensure some padding and avoid division by zero
    temp_range = max_val - min_val
    if temp_range == 0:
        temp_range = 1 # Avoid division by zero if all temps are the same

    chart_width = console.width - 20 # Allocate some space for labels
    if chart_width < 10:
        chart_width = 10 # Minimum width

    chart_lines = []
    chart_lines.append(Text(f"[bold blue]Daily Temperature Chart in {timezone} ({temp_unit})[/bold blue]"))
    chart_lines.append(Text(""))

    for i, day in enumerate(times):
        max_t = max_temps[i]
        min_t = min_temps[i]

        # Normalize temperatures to chart width
        max_norm = int(((max_t - min_val) / temp_range) * chart_width)
        min_norm = int(((min_t - min_val) / temp_range) * chart_width)

        # Ensure min_norm is always less than or equal to max_norm
        if min_norm > max_norm:
            min_norm = max_norm

        # Create the bar
        bar = Text("", style="white")
        # Add leading spaces for alignment based on min_norm
        bar.append(" " * min_norm)
        # Add min temp part (blue)
        bar.append("█" * (max_norm - min_norm), style="blue")
        # Add max temp part (red)
        bar.append("█", style="red") # Represent max temp with a single red block

        # Format the line: Date | Min Temp - Max Temp | [Chart Bar]
        line = Text.from_markup(f"[cyan]{day}[/cyan] | [blue]{min_t:.1f}[/blue] - [red]{max_t:.1f}[/red] {temp_unit} | ")
        line.append(bar)
        chart_lines.append(line)

    chart_lines.append(Text(""))
    chart_lines.append(Text(f"[blue]Min Temp[/blue] [red]Max Temp[/red]"))

    # Join the Text objects with newlines before passing to Panel
    final_text_content = Text("\n").join(chart_lines)
    console.print(Panel(final_text_content, box=box.ROUNDED))

def display_error(message: str):
    """Displays an error message using rich.

    Args:
        message (str): The error message to display.
    """
    console.print(Panel(f"[bold red]Error:[/bold red] {message}", title="[bold red]Application Error[/bold red]"))

def display_message(message: str):
    """Displays a general message using rich.

    Args:
        message (str): The message to display.
    """
    console.print(Panel(f"[bold green]Info:[/bold green] {message}", title="[bold green]Information[/bold green]"))
