from datetime import date, datetime, time, timedelta
from pathlib import Path

import pytest

from er_triage.models import EmergencyQueue, Patient, TriageAssessment
from er_triage.repository import load_patients
from tests.conftest import make_patient, today_at

SAMPLE_DATA = Path(__file__).parent.parent / "data" / "sample_data.jsonl"


def test_new_patient_is_not_flagged_for_reassessment():
    patient = make_patient("F001", 70, "Dizziness", 3)

    assert patient.needs_reassessment is False
    assert patient.reassessment_reason is None


def test_flag_for_reassessment_marks_waiting_patient_with_reason():
    patient = make_patient("F001", 70, "Dizziness", 3)

    patient.flag_for_reassessment("heat:danger")

    assert patient.needs_reassessment is True
    assert patient.reassessment_reason == "heat:danger"


def test_start_treatment_clears_reassessment_flag():
    patient = make_patient("F001", 70, "Dizziness", 3)
    patient.flag_for_reassessment("heat:danger")

    patient.start_treatment()

    assert patient.status == "in_treatment"
    assert patient.needs_reassessment is False
    assert patient.reassessment_reason is None


@pytest.mark.parametrize("status", ["in_treatment", "completed"])
def test_patient_who_is_not_waiting_cannot_be_flagged(status):
    patient = make_patient("F001", 70, "Dizziness", 3, status=status)

    with pytest.raises(ValueError, match="waiting"):
        patient.flag_for_reassessment("heat:danger")

    assert patient.needs_reassessment is False


def test_patients_loaded_from_sample_file_are_not_flagged():
    patients = load_patients(SAMPLE_DATA)

    assert len(patients) == 15
    assert all(not patient.needs_reassessment for patient in patients)

def on_day(days_from_today):
    return datetime.combine(date.today() + timedelta(days=days_from_today), time(6, 0)).isoformat()


@pytest.mark.parametrize("pain_level", [-1, 11, 2.5, True])
def test_invalid_pain_level_raises_value_error(pain_level):
    with pytest.raises(ValueError, match="Pain level"):
        TriageAssessment("Headache", pain_level, 3)


@pytest.mark.parametrize("urgency_level", [0, 6, "1"])
def test_invalid_urgency_level_raises_value_error(urgency_level):
    with pytest.raises(ValueError, match="Urgency level"):
        TriageAssessment("Headache", 3, urgency_level)


def test_arrival_time_that_is_not_a_date_raises_value_error():
    with pytest.raises(ValueError, match="Invalid arrival time"):
        Patient("P100", "Test Patient", 30, "not-a-date", TriageAssessment("Headache", 3, 4))


@pytest.mark.parametrize("arrival_time", [on_day(-1), on_day(1), "2020-01-01T10:00:00"])
def test_arrival_time_that_is_not_today_raises_value_error(arrival_time):
    with pytest.raises(ValueError, match="must be today"):
        Patient("P100", "Test Patient", 30, arrival_time, TriageAssessment("Headache", 3, 4))


def test_arrival_time_today_is_accepted():
    patient = Patient("P100", "Test Patient", 30, today_at(6, 30), TriageAssessment("Headache", 3, 4))

    assert patient.arrival_time == today_at(6, 30)


def test_adding_the_same_patient_twice_raises_value_error():
    queue = EmergencyQueue()
    patient = make_patient("Q001", 40, "Headache", 3)
    queue.add_patient(patient)

    with pytest.raises(ValueError, match="already in the queue"):
        queue.add_patient(patient)

    assert len(queue) == 1


def test_get_next_patient_returns_most_urgent_and_starts_treatment():
    queue = EmergencyQueue()
    queue.add_patient(make_patient("Q001", 40, "Headache", 3, arrival_time=today_at(6, 0)))
    queue.add_patient(make_patient("Q002", 40, "Chest pain", 1, arrival_time=today_at(6, 30)))

    next_patient = queue.get_next_patient()

    assert next_patient.patient_id == "Q002"
    assert next_patient.status == "in_treatment"
    assert len(queue) == 1


def test_get_next_patient_from_empty_queue_returns_none():
    assert EmergencyQueue().get_next_patient() is None


def test_equal_urgency_is_ordered_by_arrival_time():
    queue = EmergencyQueue()
    queue.add_patient(make_patient("Q001", 40, "Headache", 3, arrival_time=today_at(6, 30)))
    queue.add_patient(make_patient("Q002", 40, "Back pain", 3, arrival_time=today_at(6, 0)))

    assert [patient.patient_id for patient in queue.patients] == ["Q002", "Q001"]


def test_updating_urgency_reorders_the_queue():
    queue = EmergencyQueue()
    first = make_patient("Q001", 40, "Headache", 3, arrival_time=today_at(6, 0))
    second = make_patient("Q002", 40, "Back pain", 2, arrival_time=today_at(6, 30))
    queue.add_patient(first)
    queue.add_patient(second)

    queue.update_patient_urgency(first, 1)

    assert [patient.patient_id for patient in queue.patients] == ["Q001", "Q002"]