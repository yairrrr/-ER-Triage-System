from datetime import date, datetime, time

import pytest
from er_triage.models import Patient, TriageAssessment


def today_at(hour, minute=0):
    return datetime.combine(date.today(), time(hour, minute)).isoformat()


def make_patient(patient_id, age, complaint, urgency, status="waiting",
                 arrival_time=None, pain=5):
    if arrival_time is None:
        arrival_time = today_at(6)
    return Patient(patient_id, f"Test {patient_id}", age, arrival_time,
                   TriageAssessment(complaint, pain, urgency), status)


@pytest.fixture
def heat_patients():
    return [
        make_patient("H001", 72, "Dizziness", 3),
        make_patient("H002", 52, "High fever", 3),
        make_patient("H003", 70, "Broken wrist", 4),
        make_patient("H004", 25, "Ankle injury", 4),
        make_patient("H005", 80, "Difficulty breathing", 1),
        make_patient("H006", 68, "Weakness", 2, status="in_treatment"),
    ]