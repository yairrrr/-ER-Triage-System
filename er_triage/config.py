import os

from dotenv import load_dotenv

# Values from a local .env file are added to the environment; the file itself is never committed
load_dotenv()


def read_str(name, default):
    return os.getenv(name, default)


def read_int(name, default):
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"Environment variable {name} must be a whole number, got {value!r}") from None


def read_float(name, default):
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        raise ValueError(f"Environment variable {name} must be a number, got {value!r}") from None


WEATHER_API_URL = read_str("WEATHER_API_URL", "https://api.open-meteo.com/v1/forecast")
HOSPITAL_LATITUDE = read_float("HOSPITAL_LATITUDE", 32.0853)
HOSPITAL_LONGITUDE = read_float("HOSPITAL_LONGITUDE", 34.7818)
WEATHER_TIMEOUT_SECONDS = read_float("WEATHER_TIMEOUT_SECONDS", 5.0)
WEATHER_MAX_ATTEMPTS = read_int("WEATHER_MAX_ATTEMPTS", 3)
WEATHER_BASE_DELAY = read_float("WEATHER_BASE_DELAY", 1.0)
WEATHER_FORECAST_HOURS = read_int("WEATHER_FORECAST_HOURS", 6)
WEATHER_SAMPLE_FILE = read_str("WEATHER_SAMPLE_FILE", "data/weather_sample.json")
LOG_LEVEL = read_str("LOG_LEVEL", "INFO")