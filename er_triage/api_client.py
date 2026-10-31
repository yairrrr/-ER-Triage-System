import logging
import time
from datetime import datetime

import requests

from . import config
from .models import HourlyForecast, WeatherSnapshot

logger = logging.getLogger(__name__)

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
class OpenMeteoClient:
    def __init__(self, session, base_url=config.WEATHER_API_URL,
                 latitude=config.HOSPITAL_LATITUDE, longitude=config.HOSPITAL_LONGITUDE,
                 timeout=config.WEATHER_TIMEOUT_SECONDS, forecast_hours=config.WEATHER_FORECAST_HOURS,
                 max_attempts=config.WEATHER_MAX_ATTEMPTS, base_delay=config.WEATHER_BASE_DELAY,
                 sleep=time.sleep):
        self.session = session
        self.base_url = base_url
        self.latitude = latitude
        self.longitude = longitude
        self.timeout = timeout
        self.forecast_hours = forecast_hours
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.sleep = sleep

    def build_params(self):
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "current": "temperature_2m,apparent_temperature,relative_humidity_2m",
            "hourly": "apparent_temperature",
            "forecast_hours": self.forecast_hours,
            "timezone": "auto",
        }

    def send_with_retry(self):
        # Only communication failures are retried; HTTP errors and invalid data would fail again
        for attempt in range(1, self.max_attempts + 1):
            try:
                return self.session.get(self.base_url, params=self.build_params(), timeout=self.timeout)
            except (requests.Timeout, requests.ConnectionError) as error:
                logger.warning("Weather request attempt %d of %d failed: %s",
                               attempt, self.max_attempts, type(error).__name__)
                if attempt == self.max_attempts:
                    raise WeatherConnectionError(
                        f"Weather service unreachable after {self.max_attempts} attempts"
                    ) from error
                self.sleep(self.base_delay * 2 ** (attempt - 1))

    def get_weather(self):
        response = self.send_with_retry()

        try:
            response.raise_for_status()
        except requests.HTTPError as error:
            logger.warning("Weather service returned HTTP %s", response.status_code)
            raise WeatherHTTPError(f"Weather service returned HTTP {response.status_code}") from error

        try:
            payload = response.json()
        except ValueError as error:
            logger.warning("Weather service returned invalid JSON")
            raise WeatherDataError("Weather service returned invalid JSON") from error

        try:
            snapshot = parse_weather_payload(payload, "live")
        except WeatherDataError as error:
            logger.warning("Weather response failed validation: %s", error)
            raise

        logger.info("Weather received: apparent temperature %.1f°C at %s",
                    snapshot.apparent_temperature_c, snapshot.observed_at)
        return snapshot