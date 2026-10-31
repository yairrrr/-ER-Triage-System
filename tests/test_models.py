from pathlib import Path

import pytest

from er_triage.repository import load_patients
from tests.conftest import make_patient

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