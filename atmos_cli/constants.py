OPEN_METEO_BASE_URL = "https://api.open-meteo.com/v1/forecast"
GEOCODING_API_URL = "https://geocoding-api.open-meteo.com/v1/search"
DEFAULT_LATITUDE = 52.52
DEFAULT_LONGITUDE = 13.41
DEFAULT_TIMEZONE = "America/New_York"
DEFAULT_FORECAST_DAYS = 7
DEFAULT_PAST_DAYS = 0

# Units
TEMPERATURE_UNITS = ["celsius", "fahrenheit"]
WIND_SPEED_UNITS = ["kmh", "ms", "mph", "kn"]
PRECIPITATION_UNITS = ["mm", "inch"]

# Time formats
TIME_FORMATS = ["iso8601", "unixtime"]

# Weather models
WEATHER_MODELS = [
    "ecmwf_ifs", "gfs_seamless", "icon_global", "icon_eu", "icon_d2",
    "gem_global", "meteofrance_arome_fwd", "meteofrance_arome_hres",
    "meteofrance_arome_fwd_seamless", "meteofrance_arome_hres_seamless",
    "arpae_cosmo_seamless", "arpae_cosmo_d2_seamless", "arpae_cosmo_5m_seamless",
    "dwd_icon_seamless", "dwd_icon_eu_seamless", "dwd_icon_d2_seamless",
    "hrrr", "era5_seamless", "era5_land_seamless", "cma_grapes_global",
    "bom_access_global", "nz_met_ensemble", "gfs_graphical", "gfs_hrrr_blend"
]

# Cell selection options
CELL_SELECTION_OPTIONS = ["land", "sea", "nearest"]

# Weather variables
HOURLY_WEATHER_VARIABLES = [
    "temperature_2m", "relative_humidity_2m", "dew_point_2m", "apparent_temperature",
    "precipitation_probability", "precipitation", "rain", "showers", "snowfall",
    "weather_code", "surface_pressure", "cloud_cover", "cloud_cover_low",
    "cloud_cover_mid", "cloud_cover_high", "visibility", "evapotranspiration",
    "et0_fao_evapotranspiration", "vapor_pressure_deficit", "wind_speed_10m",
    "wind_speed_80m", "wind_speed_120m", "wind_speed_180m", "wind_direction_10m",
    "wind_direction_80m", "wind_direction_120m", "wind_direction_180m",
    "wind_gusts_10m", "temperature_80m", "temperature_120m", "temperature_180m",
    "soil_temperature_0cm", "soil_temperature_6cm", "soil_temperature_18cm",
    "soil_temperature_54cm", "soil_moisture_0_1cm", "soil_moisture_1_3cm",
    "soil_moisture_3_9cm", "soil_moisture_9_27cm", "soil_moisture_27_81cm"
]

DAILY_WEATHER_VARIABLES = [
    "weather_code", "temperature_2m_max", "temperature_2m_min",
    "apparent_temperature_max", "apparent_temperature_min", "sunrise", "sunset",
    "daylight_duration", "sunshine_duration", "uv_index_max", "uv_index_clear_sky_max",
    "precipitation_sum", "rain_sum", "showers_sum", "snowfall_sum",
    "precipitation_hours", "wind_speed_10m_max", "wind_gusts_10m_max",
    "wind_direction_10m_dominant"
]

CURRENT_WEATHER_VARIABLES = [
    "temperature_2m", "relative_humidity_2m", "apparent_temperature",
    "is_day", "precipitation", "rain", "showers", "snowfall",
    "weather_code", "cloud_cover", "pressure_msl", "surface_pressure",
    "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m"
]

ARCHIVE_BASE_URL = "https://archive-api.open-meteo.com/v1/archive"

# WMO Weather interpretation codes (WWMO)
WEATHER_CODES = {
    0: "Clear sky",
    1: "Mostly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Drizzle: Light",
    53: "Drizzle: Moderate",
    55: "Drizzle: Dense intensity",
    56: "Freezing Drizzle: Light",
    57: "Freezing Drizzle: Dense intensity",
    61: "Rain: Slight",
    63: "Rain: Moderate",
    65: "Rain: Heavy intensity",
    66: "Freezing Rain: Light",
    67: "Freezing Rain: Heavy intensity",
    71: "Snow fall: Slight",
    73: "Snow fall: Moderate",
    75: "Snow fall: Heavy intensity",
    77: "Snow grains",
    80: "Rain showers: Slight",
    81: "Rain showers: Moderate",
    82: "Rain showers: Violent",
    85: "Snow showers: Slight",
    86: "Snow showers: Heavy",
    95: "Thunderstorm: Slight or moderate",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail"
}