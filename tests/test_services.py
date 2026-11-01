import logging
from pathlib import Path
from unittest.mock import Mock

import pytest

from er_triage.api_client import WeatherConnectionError, WeatherDataError, WeatherHTTPError
from er_triage.models import HourlyForecast, WeatherSnapshot
from er_triage.observers import AuditLogObserver, EventPublisher, ReassessmentWorklist
from er_triage.repository import load_patients
from er_triage.services import HeatAlertService, classify_heat_level
from er_triage.strategies import AllAtRiskStrategy, NoFlaggingStrategy, VulnerableOnlyStrategy

SAMPLE_DATA = Path(__file__).parent.parent / "data" / "sample_data.jsonl"

@pytest.mark.parametrize("apparent_temperature, expected_level", [
    (20, "normal"),
    (31.9, "normal"),
    (32, "caution"),
    (38.9, "caution"),
    (39, "danger"),
    (45, "danger"),
])
def test_classify_heat_level(apparent_temperature, expected_level):
    assert classify_heat_level(apparent_temperature) == expected_level
def snapshot_with(apparent_temperature):
    return WeatherSnapshot("2026-07-20T13:00", apparent_temperature - 3, apparent_temperature, 50,
                           (HourlyForecast("2026-07-20T13:00", apparent_temperature),), "simulated")


def client_returning(apparent_temperature):
    client = Mock()
    client.get_weather.return_value = snapshot_with(apparent_temperature)
    return client


def client_failing_with(error):
    client = Mock()
    client.get_weather.side_effect = error
    return client


def build_service(weather_client):
    publisher = EventPublisher()
    audit_log = AuditLogObserver()
    worklist = ReassessmentWorklist()
    publisher.subscribe(audit_log)
    publisher.subscribe(worklist)
    strategies = {
        "normal": NoFlaggingStrategy(),
        "caution": VulnerableOnlyStrategy(),
        "danger": AllAtRiskStrategy(),
    }
    return HeatAlertService(weather_client, publisher, strategies), audit_log, worklist


def flagged_ids(patients):
    return [patient.patient_id for patient in patients if patient.needs_reassessment]


@pytest.mark.parametrize("apparent_temperature, expected_level, expected_ids", [
    (40, "danger", ["H001", "H002", "H003"]),
    (35, "caution", ["H001"]),
    (25, "normal", []),
])
def test_patients_are_flagged_according_to_the_heat_level(heat_patients, apparent_temperature,
                                                          expected_level, expected_ids):
    service, _, _ = build_service(client_returning(apparent_temperature))

    result = service.run_check(heat_patients)

    assert result.status == "applied"
    assert result.heat_level == expected_level
    assert result.flagged_patient_ids == expected_ids
    assert flagged_ids(heat_patients) == expected_ids


def test_flagged_patients_reach_both_observers(heat_patients):
    service, audit_log, worklist = build_service(client_returning(40))

    service.run_check(heat_patients)

    assert len(audit_log.entries) == 3
    assert [patient.patient_id for patient in worklist.pending()] == ["H001", "H002", "H003"]
    assert heat_patients[1].reassessment_reason == "heat:danger"


@pytest.mark.parametrize("error", [
    WeatherConnectionError("unreachable after 3 attempts"),
    WeatherHTTPError("HTTP 500"),
    WeatherDataError("missing apparent_temperature"),
])
def test_weather_failure_flags_nobody(heat_patients, error):
    service, audit_log, worklist = build_service(client_failing_with(error))

    result = service.run_check(heat_patients)

    assert result.status == "unavailable"
    assert result.heat_level is None
    assert result.flagged_patient_ids == []
    assert result.error_message == str(error)
    assert flagged_ids(heat_patients) == []
    assert audit_log.entries == []
    assert worklist.pending() == []


def test_weather_failure_is_logged_as_warning(heat_patients, caplog):
    service, _, _ = build_service(client_failing_with(WeatherConnectionError("unreachable")))

    with caplog.at_level(logging.WARNING, logger="er_triage.services"):
        service.run_check(heat_patients)

    assert "weather data unavailable" in caplog.text


def test_unexpected_error_is_not_hidden_as_unavailable(heat_patients):
    service, _, _ = build_service(client_failing_with(RuntimeError("bug in our code")))

    with pytest.raises(RuntimeError):
        service.run_check(heat_patients)


def test_second_check_does_not_flag_or_publish_again(heat_patients):
    service, audit_log, _ = build_service(client_returning(40))
    service.run_check(heat_patients)

    second_result = service.run_check(heat_patients)

    assert second_result.flagged_patient_ids == []
    assert len(audit_log.entries) == 3


@pytest.mark.parametrize("apparent_temperature, expected_ids", [
    (40, ["P005", "P011"]),
    (35, ["P011"]),
])
def test_sample_data_gives_the_results_the_group_defined(apparent_temperature, expected_ids):
    patients = load_patients(SAMPLE_DATA)
    service, _, _ = build_service(client_returning(apparent_temperature))

    result = service.run_check(patients)

    assert result.flagged_patient_ids == expected_ids


def test_service_requires_a_strategy_for_every_heat_level():
    with pytest.raises(ValueError, match="caution"):
        HeatAlertService(Mock(), EventPublisher(), {"normal": NoFlaggingStrategy(), "danger": AllAtRiskStrategy()})