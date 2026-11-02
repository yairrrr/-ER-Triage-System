import json
import logging
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, call

import pytest
import main as demo

from er_triage.api_client import OfflineWeatherClient, WeatherConnectionError
from er_triage.models import EmergencyQueue
from er_triage.reporting import generate_heat_report
from er_triage.repository import load_patients
from main import build_heat_service
from er_triage.models import HourlyForecast, WeatherSnapshot
from tests.conftest import make_patient, today_at


SAMPLE_DATA = Path(__file__).parent.parent / "data" / "sample_data.jsonl"


def patient_state(patients):
    return [
        (patient.patient_id, patient.assessment.urgency_level, patient.status,
         patient.needs_reassessment, patient.reassessment_reason)
        for patient in patients
    ]


def queue_for(patients):
    queue = EmergencyQueue()
    for patient in patients:
        queue.add_patient(patient)
    return queue


def test_offline_heat_check_connects_patients_observers_and_report(tmp_path):
    payload = {
        "current": {
            "time": "2026-07-20T13:00", "temperature_2m": 36.8,
            "apparent_temperature": 40.5, "relative_humidity_2m": 48,
        },
        "hourly": {
            "time": ["2026-07-20T13:00", "2026-07-20T15:00"],
            "apparent_temperature": [40.5, 42.0],
        },
    }
    weather_file = tmp_path / "weather.json"
    weather_file.write_text(json.dumps(payload), encoding="utf-8")
    patients = load_patients(SAMPLE_DATA)
    queue = queue_for(patients)
    before = patient_state(patients)
    queue_order = [patient.patient_id for patient in queue.patients]
    service, audit_log, worklist = build_heat_service(OfflineWeatherClient(weather_file))

    result = service.run_check(patients)
    report = generate_heat_report(patients, result)

    assert result.status == "applied"
    assert result.flagged_patient_ids == ["P005", "P011"]
    assert [patient.patient_id for patient in patients if patient.needs_reassessment] == ["P005", "P011"]
    assert all(patient.reassessment_reason == "heat:danger" for patient in worklist.pending())
    expected_worklist = sorted(
        [patient for patient in patients if patient.patient_id in ("P005", "P011")],
        key=lambda patient: (patient.assessment.urgency_level, patient.arrival_time),
    )
    assert worklist.pending() == expected_worklist
    assert audit_log.entries == [
        "Patient P005 flagged for reassessment (heat level: danger)",
        "Patient P011 flagged for reassessment (heat level: danger)",
    ]
    assert report == {
        "data_source": "simulated", "status": "applied", "heat_level": "danger",
        "observed_at": "2026-07-20T13:00", "apparent_temperature_c": 40.5,
        "forecast_max_c": 42.0, "forecast_max_time": "2026-07-20T15:00",
        "forecast_level": "danger", "flagged_count": 2,
        "flagged_patient_ids": ["P005", "P011"], "error_message": None,
    }
    assert [state[:3] for state in patient_state(patients)] == [state[:3] for state in before]
    assert [patient.patient_id for patient in queue.patients] == queue_order


def test_weather_failure_leaves_patients_queue_and_observers_unchanged(caplog):
    class FailingClient:
        def get_weather(self):
            raise WeatherConnectionError("Simulated connection failure")

    patients = load_patients(SAMPLE_DATA)
    queue = queue_for(patients)
    before = patient_state(patients)
    queue_order = [patient.patient_id for patient in queue.patients]
    service, audit_log, worklist = build_heat_service(FailingClient())

    with caplog.at_level(logging.WARNING, logger="er_triage.services"):
        result = service.run_check(patients)
    report = generate_heat_report(patients, result)

    assert result.status == "unavailable"
    assert result.snapshot is None
    assert result.flagged_patient_ids == []
    assert patient_state(patients) == before
    assert [patient.patient_id for patient in queue.patients] == queue_order
    assert worklist.pending() == []
    assert audit_log.entries == []
    assert "weather data unavailable" in caplog.text
    assert report == {
        "data_source": "unavailable", "status": "unavailable", "heat_level": None,
        "observed_at": None, "apparent_temperature_c": None, "forecast_max_c": None,
        "forecast_max_time": None, "forecast_level": None, "flagged_count": 0,
        "flagged_patient_ids": [], "error_message": "Simulated connection failure",
    }


def test_worklist_sorts_unsorted_patients_by_urgency_then_arrival():
    patients = [
        make_patient("S003", 70, "Dizziness", 4, arrival_time=today_at(6)),
        make_patient("S002", 70, "Dizziness", 2, arrival_time=today_at(7)),
        make_patient("S001", 70, "Dizziness", 2, arrival_time=today_at(6)),
    ]
    snapshot = WeatherSnapshot("2026-07-20T13:00", 36, 40, 48,
                               (HourlyForecast("2026-07-20T14:00", 42),), "simulated")
    client = Mock()
    client.get_weather.return_value = snapshot
    service, _, worklist = build_heat_service(client)
    before = patient_state(patients)
    queue = queue_for(patients)
    queue_order = [patient.patient_id for patient in queue.patients]

    service.run_check(patients)

    assert [patient.patient_id for patient in worklist.pending()] == ["S001", "S002", "S003"]
    assert [state[:3] for state in patient_state(patients)] == [state[:3] for state in before]
    assert [patient.patient_id for patient in queue.patients] == queue_order


@pytest.mark.parametrize("arguments, live", [([], False), (["--live"], True)])
def test_main_dispatches_stages_and_configures_logging(monkeypatch, arguments, live):
    calls = Mock()
    monkeypatch.setattr("sys.argv", ["main.py", *arguments])
    monkeypatch.setattr(demo, "run_stage1_demo", calls.stage1)
    monkeypatch.setattr(demo, "run_stage2_demo", calls.stage2)
    configure_logging = Mock()
    monkeypatch.setattr(demo.logging, "basicConfig", configure_logging)

    demo.main()

    assert calls.mock_calls == [call.stage1(), call.stage2(live)]
    configure_logging.assert_called_once_with(level=demo.config.LOG_LEVEL)


@pytest.mark.parametrize("live, fails", [(False, False), (True, False), (True, True)])
def test_stage2_selects_client_without_fallback_and_prints_in_order(monkeypatch, capsys, live, fails):
    source = "live" if live else "simulated"
    client = Mock()
    if fails:
        client.get_weather.side_effect = WeatherConnectionError("Mock live connection failure")
    else:
        client.get_weather.return_value = WeatherSnapshot(
            "2026-07-20T13:00", 36.8, 40.5, 48,
            (HourlyForecast("2026-07-20T15:00", 42.0),), source,
        )
    offline_factory = Mock(return_value=client)
    live_factory = Mock(return_value=client)
    session_factory = MagicMock()
    monkeypatch.setattr(demo, "OfflineWeatherClient", offline_factory)
    monkeypatch.setattr(demo, "OpenMeteoClient", live_factory)
    monkeypatch.setattr(demo.requests, "Session", session_factory)
    monkeypatch.setattr(demo, "load_patients", Mock(side_effect=lambda path: load_patients(SAMPLE_DATA)))
    monkeypatch.setattr(demo, "load_lab_data", Mock(return_value={}))
    sequential = AsyncMock(return_value=[])
    concurrent = AsyncMock(return_value=[])
    monkeypatch.setattr(demo, "collect_lab_results_sequential", sequential)
    monkeypatch.setattr(demo, "collect_lab_results_concurrent", concurrent)

    demo.run_stage2_demo(live)

    output = capsys.readouterr().out
    client.get_weather.assert_called_once_with()
    if live:
        offline_factory.assert_not_called()
        session_factory.assert_called_once_with()
        live_factory.assert_called_once_with(
            session_factory.return_value.__enter__.return_value,
            base_url=demo.config.WEATHER_API_URL,
            latitude=demo.config.HOSPITAL_LATITUDE, longitude=demo.config.HOSPITAL_LONGITUDE,
            timeout=demo.config.WEATHER_TIMEOUT_SECONDS,
            forecast_hours=demo.config.WEATHER_FORECAST_HOURS,
            max_attempts=demo.config.WEATHER_MAX_ATTEMPTS, base_delay=demo.config.WEATHER_BASE_DELAY,
        )
        source_line = "[DATA SOURCE: LIVE – Open-Meteo]"
    else:
        live_factory.assert_not_called()
        session_factory.assert_not_called()
        offline_factory.assert_called_once_with(demo.config.WEATHER_SAMPLE_FILE)
        source_line = f"[DATA SOURCE: SIMULATED – {demo.config.WEATHER_SAMPLE_FILE}]"
    markers = [source_line, "Heat level:", "Flagged patient IDs:", "Audit log:",
               "Nurse worklist:", "Heat report:", "=== Weather Failure [SIMULATED] ===",
               "=== Lab Results [SIMULATED] ===", "Sequential results:", "Sequential seconds:",
               "Concurrent results:", "Concurrent seconds:", "=== Nurse Claims [SIMULATED] ===",
               "Claimed patient IDs:", "Remaining worklist: []"]
    positions = [output.index(marker) for marker in markers]
    assert positions == sorted(positions)
    primary_output, failure_output = output.split("=== Weather Failure [SIMULATED] ===", 1)
    if fails:
        assert "Flagged patient IDs: []" in primary_output
        assert "'status': 'unavailable'" in primary_output
        assert "No patients in the nurse worklist; the Threads demo made no actual claims." in output
        assert "'data_source': 'simulated'" not in primary_output
    else:
        assert "P005 heat:danger" in primary_output
        assert "P011 heat:danger" in primary_output
        assert f"'data_source': '{source}'" in primary_output
        assert "the Threads demo made no actual claims" not in output
    assert "Flagged patient IDs: []" in failure_output
    assert "'status': 'unavailable'" in failure_output
    sequential.assert_awaited_once()
    concurrent.assert_awaited_once()
