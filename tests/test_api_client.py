import copy

import pytest

from er_triage.api_client import WeatherDataError, parse_weather_payload

# Based on a real Open-Meteo response received on 2026-10-29
VALID_PAYLOAD = {
    "current": {
        "time": "2026-10-29T20:15",
        "interval": 900,
        "temperature_2m": 22.7,
        "apparent_temperature": 24.0,
        "relative_humidity_2m": 68,
    },
    "hourly": {
        "time": [
            "2026-10-29T20:00", "2026-10-29T21:00", "2026-10-29T22:00",
            "2026-10-29T23:00", "2026-10-30T00:00", "2026-10-30T01:00",
        ],
        "apparent_temperature": [23.9, 23.5, 23.0, 22.6, 21.7, 20.9],
    },
}

MISSING = object()


@pytest.fixture
def payload():
    return copy.deepcopy(VALID_PAYLOAD)


def test_valid_payload_is_converted_to_snapshot(payload):
    snapshot = parse_weather_payload(payload, "live")

    assert snapshot.observed_at == "2026-10-29T20:15"
    assert snapshot.temperature_c == 22.7
    assert snapshot.apparent_temperature_c == 24.0
    assert snapshot.humidity_percent == 68
    assert snapshot.source == "live"
    assert len(snapshot.forecast) == 6
    assert snapshot.forecast[0].time == "2026-10-29T20:00"
    assert snapshot.forecast[0].apparent_temperature_c == 23.9


@pytest.mark.parametrize("field, bad_value", [
    ("apparent_temperature", MISSING),
    ("apparent_temperature", "hot"),
    ("temperature_2m", True),
    ("temperature_2m", 500),
    ("relative_humidity_2m", 120),
    ("time", "yesterday"),
])
def test_invalid_current_field_raises_weather_data_error(payload, field, bad_value):
    if bad_value is MISSING:
        del payload["current"][field]
    else:
        payload["current"][field] = bad_value

    with pytest.raises(WeatherDataError, match=field):
        parse_weather_payload(payload, "live")


@pytest.mark.parametrize("section", ["current", "hourly"])
def test_missing_section_raises_weather_data_error(payload, section):
    del payload[section]

    with pytest.raises(WeatherDataError, match=section):
        parse_weather_payload(payload, "live")


def test_forecast_lists_with_different_length_raise_weather_data_error(payload):
    payload["hourly"]["apparent_temperature"].pop()

    with pytest.raises(WeatherDataError, match="same length"):
        parse_weather_payload(payload, "live")


def test_null_forecast_value_raises_weather_data_error(payload):
    payload["hourly"]["apparent_temperature"][2] = None

    with pytest.raises(WeatherDataError, match="index 2"):
        parse_weather_payload(payload, "live")


def test_payload_that_is_not_an_object_raises_weather_data_error():
    with pytest.raises(WeatherDataError):
        parse_weather_payload([], "live")