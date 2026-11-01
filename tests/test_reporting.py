import pytest

from er_triage.models import HourlyForecast, WeatherSnapshot
from er_triage.reporting import generate_heat_report, generate_waiting_report
from er_triage.services import HeatCheckResult, summarize_forecast
from tests.conftest import make_patient

FORECAST = (
    HourlyForecast("2026-07-20T13:00", 40.5),
    HourlyForecast("2026-07-20T14:00", 41.6),
    HourlyForecast("2026-07-20T15:00", 42.0),
    HourlyForecast("2026-07-20T16:00", 41.2),
)
SNAPSHOT = WeatherSnapshot("2026-07-20T13:00", 36.8, 40.5, 48, FORECAST, "simulated")


def test_summarize_forecast_returns_peak_hour_and_expected_level():
    assert summarize_forecast(FORECAST) == {
        "max_apparent_temperature_c": 42.0,
        "time": "2026-07-20T15:00",
        "expected_level": "danger",
    }


def test_summarize_forecast_keeps_earliest_hour_when_peak_repeats():
    forecast = (
        HourlyForecast("2026-07-20T13:00", 30.0),
        HourlyForecast("2026-07-20T14:00", 33.0),
        HourlyForecast("2026-07-20T15:00", 33.0),
    )

    summary = summarize_forecast(forecast)

    assert summary["time"] == "2026-07-20T14:00"
    assert summary["expected_level"] == "caution"


def test_summarize_forecast_rejects_empty_forecast():
    with pytest.raises(ValueError, match="at least one hour"):
        summarize_forecast(())


def test_heat_report_after_applied_check():
    flagged = make_patient("R001", 72, "Dizziness", 3)
    flagged.flag_for_reassessment("heat:danger")
    not_flagged = make_patient("R002", 30, "Ankle injury", 4)
    result = HeatCheckResult("applied", "danger", SNAPSHOT, ["R001"], None)

    report = generate_heat_report([flagged, not_flagged], result)

    assert report == {
        "data_source": "simulated",
        "status": "applied",
        "heat_level": "danger",
        "observed_at": "2026-07-20T13:00",
        "apparent_temperature_c": 40.5,
        "forecast_max_c": 42.0,
        "forecast_max_time": "2026-07-20T15:00",
        "forecast_level": "danger",
        "flagged_count": 1,
        "flagged_patient_ids": ["R001"],
        "error_message": None,
    }


def test_heat_report_when_weather_is_unavailable():
    patients = [make_patient("R001", 72, "Dizziness", 3)]
    result = HeatCheckResult("unavailable", None, None, [], "Weather service unreachable after 3 attempts")

    report = generate_heat_report(patients, result)

    assert report["data_source"] == "unavailable"
    assert report["heat_level"] is None
    assert report["apparent_temperature_c"] is None
    assert report["forecast_max_c"] is None
    assert report["flagged_count"] == 0
    assert report["error_message"] == "Weather service unreachable after 3 attempts"


def test_patient_who_started_treatment_is_not_counted_in_heat_report():
    patient = make_patient("R001", 72, "Dizziness", 3)
    patient.flag_for_reassessment("heat:danger")
    patient.start_treatment()

    report = generate_heat_report([patient], HeatCheckResult("applied", "danger", SNAPSHOT, ["R001"], None))

    assert report["flagged_count"] == 0
    assert report["flagged_patient_ids"] == []


def test_waiting_report_from_stage_1_still_counts_only_waiting_patients():
    waiting = make_patient("R001", 40, "Headache", 3)
    in_treatment = make_patient("R002", 40, "Headache", 3, status="in_treatment")

    report = generate_waiting_report([waiting, in_treatment])

    assert report["total_waiting"] == 1
    assert [patient["patient_id"] for patient in report["waiting_patients"]] == ["R001"]