import copy
import logging
from unittest.mock import Mock, call

import pytest
import requests

from er_triage.api_client import (
    OpenMeteoClient,
    WeatherConnectionError,
    WeatherDataError,
    WeatherHTTPError,
    parse_weather_payload,
)
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

BASE_URL = "https://weather.example.test/forecast"


def make_response(payload=None, status_code=200, json_error=None):
    response = Mock()
    response.status_code = status_code
    if status_code >= 400:
        response.raise_for_status.side_effect = requests.HTTPError(f"{status_code} Error")
    if json_error is not None:
        response.json.side_effect = json_error
    else:
        response.json.return_value = copy.deepcopy(VALID_PAYLOAD) if payload is None else payload
    return response


@pytest.fixture
def session():
    return Mock()


@pytest.fixture
def sleep():
    return Mock()


@pytest.fixture
def client(session, sleep):
    return OpenMeteoClient(session, base_url=BASE_URL, latitude=32.0853, longitude=34.7818,
                           timeout=5, forecast_hours=6, max_attempts=3, base_delay=1.0, sleep=sleep)


def test_successful_request_returns_live_snapshot(client, session, sleep):
    session.get.return_value = make_response()

    snapshot = client.get_weather()

    assert snapshot.source == "live"
    assert snapshot.apparent_temperature_c == 24.0
    session.get.assert_called_once()
    assert session.get.call_args.args[0] == BASE_URL
    assert session.get.call_args.kwargs["timeout"] == 5
    params = session.get.call_args.kwargs["params"]
    assert params["current"] == "temperature_2m,apparent_temperature,relative_humidity_2m"
    assert params["forecast_hours"] == 6
    sleep.assert_not_called()


def test_timeout_then_success_retries_once(client, session, sleep):
    session.get.side_effect = [requests.Timeout(), make_response()]

    snapshot = client.get_weather()

    assert snapshot.source == "live"
    assert session.get.call_count == 2
    sleep.assert_called_once_with(1.0)


def test_connection_errors_stop_after_three_attempts(client, session, sleep):
    session.get.side_effect = requests.ConnectionError()

    with pytest.raises(WeatherConnectionError, match="3 attempts"):
        client.get_weather()

    assert session.get.call_count == 3
    assert sleep.call_args_list == [call(1.0), call(2.0)]


def test_each_failed_attempt_is_logged(client, session, caplog):
    session.get.side_effect = requests.Timeout()

    with caplog.at_level(logging.WARNING, logger="er_triage.api_client"):
        with pytest.raises(WeatherConnectionError):
            client.get_weather()

    assert [record.getMessage() for record in caplog.records] == [
        "Weather request attempt 1 of 3 failed: Timeout",
        "Weather request attempt 2 of 3 failed: Timeout",
        "Weather request attempt 3 of 3 failed: Timeout",
    ]


@pytest.mark.parametrize("status_code", [401, 404, 500])
def test_http_error_is_not_retried(client, session, sleep, status_code):
    session.get.return_value = make_response(status_code=status_code)

    with pytest.raises(WeatherHTTPError, match=str(status_code)):
        client.get_weather()

    assert session.get.call_count == 1
    sleep.assert_not_called()


def test_invalid_json_is_not_retried(client, session, sleep):
    session.get.return_value = make_response(json_error=ValueError("Expecting value"))

    with pytest.raises(WeatherDataError, match="invalid JSON"):
        client.get_weather()

    assert session.get.call_count == 1
    sleep.assert_not_called()


def test_missing_required_field_is_not_retried(client, session, sleep):
    broken_payload = copy.deepcopy(VALID_PAYLOAD)
    del broken_payload["current"]["apparent_temperature"]
    session.get.return_value = make_response(payload=broken_payload)

    with pytest.raises(WeatherDataError, match="apparent_temperature"):
        client.get_weather()

    assert session.get.call_count == 1
    sleep.assert_not_called()