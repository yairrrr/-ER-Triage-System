import pytest

from er_triage.observers import EventPublisher, PatientFlaggedEvent, ReassessmentWorklist
from er_triage.threaded_processing import nurses_claim_concurrently
from tests.conftest import make_patient


def worklist_with_flagged_patients(count):
    publisher = EventPublisher()
    worklist = ReassessmentWorklist()
    publisher.subscribe(worklist)
    for number in range(count):
        patient = make_patient(f"T{number:03d}", 70, "Dizziness", 3)
        patient.flag_for_reassessment("heat:danger")
        publisher.publish(PatientFlaggedEvent(patient, "danger"))
    return worklist


def all_claimed_ids(claimed_by_nurse):
    return [patient_id for claimed_ids in claimed_by_nurse.values() for patient_id in claimed_ids]


def test_four_nurses_take_five_patients_exactly_once():
    worklist = worklist_with_flagged_patients(5)

    claimed_by_nurse = nurses_claim_concurrently(worklist, ["N1", "N2", "N3", "N4"])

    claimed_ids = all_claimed_ids(claimed_by_nurse)
    assert len(claimed_ids) == 5
    assert sorted(claimed_ids) == ["T000", "T001", "T002", "T003", "T004"]
    assert worklist.pending() == []
    assert len(worklist.claims) == 5


@pytest.mark.parametrize("patient_count, nurse_count", [(1, 6), (10, 3), (0, 4), (300, 8)])
def test_every_patient_is_claimed_once_whatever_the_number_of_nurses(patient_count, nurse_count):
    worklist = worklist_with_flagged_patients(patient_count)
    nurse_ids = [f"N{number}" for number in range(nurse_count)]

    claimed_by_nurse = nurses_claim_concurrently(worklist, nurse_ids)

    claimed_ids = all_claimed_ids(claimed_by_nurse)
    assert len(claimed_ids) == patient_count
    assert len(set(claimed_ids)) == patient_count
    assert worklist.pending() == []


def test_each_claim_is_recorded_for_the_nurse_who_made_it():
    worklist = worklist_with_flagged_patients(20)

    claimed_by_nurse = nurses_claim_concurrently(worklist, ["N1", "N2", "N3"])

    for nurse_id, claimed_ids in claimed_by_nurse.items():
        for patient_id in claimed_ids:
            assert worklist.claims[patient_id] == nurse_id