from datetime import datetime

from .models import HourlyForecast, WeatherSnapshot


class WeatherServiceError(Exception):
    """Base class for every failure of the weather service."""


class WeatherConnectionError(WeatherServiceError):
    """The service could not be reached after all attempts (timeout or connection error)."""


class WeatherHTTPError(WeatherServiceError):
    """The service answered with an HTTP error status."""


class WeatherDataError(WeatherServiceError):
    """The response is not valid JSON or does not match the expected structure."""


def is_number(value):
    # bool is a subclass of int, so True/False must be rejected explicitly
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def is_iso_time(value):
    if not isinstance(value, str):
        return False
    try:
        datetime.fromisoformat(value)
    except ValueError:
        return False
    return True


def require_section(payload, name):
    section = payload.get(name)
    if not isinstance(section, dict):
        raise WeatherDataError(f"Missing or invalid section: {name!r}")
    return section


def require_number(section, section_name, field, minimum, maximum):
    value = section.get(field)
    if not is_number(value) or not minimum <= value <= maximum:
        raise WeatherDataError(f"Invalid value for {section_name}.{field}: {value!r}")
    return float(value)


def parse_weather_payload(payload, source):
    if not isinstance(payload, dict):
        raise WeatherDataError("Weather response must be a JSON object")

    current = require_section(payload, "current")
    observed_at = current.get("time")
    if not is_iso_time(observed_at):
        raise WeatherDataError(f"Invalid value for current.time: {observed_at!r}")
    temperature = require_number(current, "current", "temperature_2m", -60, 60)
    apparent_temperature = require_number(current, "current", "apparent_temperature", -60, 60)
    humidity = require_number(current, "current", "relative_humidity_2m", 0, 100)

    hourly = require_section(payload, "hourly")
    times = hourly.get("time")
    values = hourly.get("apparent_temperature")
    if not isinstance(times, list) or not times:
        raise WeatherDataError("hourly.time must be a non-empty list")
    if not isinstance(values, list) or len(values) != len(times):
        raise WeatherDataError("hourly.apparent_temperature must be a list with the same length as hourly.time")

    forecast = []
    for index, (time_value, apparent_value) in enumerate(zip(times, values)):
        if not is_iso_time(time_value) or not is_number(apparent_value) or not -60 <= apparent_value <= 60:
            raise WeatherDataError(f"Invalid hourly forecast entry at index {index}: {time_value!r}, {apparent_value!r}")
        forecast.append(HourlyForecast(time_value, float(apparent_value)))

    return WeatherSnapshot(observed_at, temperature, apparent_temperature, humidity, tuple(forecast), source)