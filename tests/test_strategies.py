from pathlib import Path

import pytest

from er_triage.repository import load_patients
from er_triage.strategies import (
    AllAtRiskStrategy,
    FlaggingStrategy,
    NoFlaggingStrategy,
    VulnerableOnlyStrategy,
    is_heat_sensitive,
)
from tests.conftest import make_patient

SAMPLE_DATA = Path(__file__).parent.parent / "data" / "sample_data.jsonl"


def selected_ids(strategy, patients):
    return [patient.patient_id for patient in strategy.select(patients)]


def test_no_flagging_strategy_selects_nobody(heat_patients):
    assert selected_ids(NoFlaggingStrategy(), heat_patients) == []


def test_vulnerable_only_strategy_needs_age_and_sensitive_complaint(heat_patients):
    assert selected_ids(VulnerableOnlyStrategy(), heat_patients) == ["H001"]


def test_all_at_risk_strategy_needs_age_or_sensitive_complaint(heat_patients):
    assert selected_ids(AllAtRiskStrategy(), heat_patients) == ["H001", "H002", "H003"]


def test_already_flagged_patient_is_not_selected_again(heat_patients):
    heat_patients[0].flag_for_reassessment("heat:caution")

    assert selected_ids(AllAtRiskStrategy(), heat_patients) == ["H002", "H003"]


@pytest.mark.parametrize("age, expected_ids", [(64, []), (65, ["A065"])])
def test_age_65_is_the_first_at_risk_age(age, expected_ids):
    patient = make_patient(f"A{age:03d}", age, "Broken wrist", 3)

    assert selected_ids(AllAtRiskStrategy(), [patient]) == expected_ids


@pytest.mark.parametrize("complaint, expected", [
    ("Dizziness", True),
    ("SHORTNESS OF BREATH", True),
    ("Sudden weakness and confusion", True),
    ("High fever", True),
    ("Ankle injury", False),
    ("Persistent vomiting", False),
])
def test_is_heat_sensitive(complaint, expected):
    patient = make_patient("S001", 30, complaint, 3)

    assert is_heat_sensitive(patient) is expected


@pytest.mark.parametrize("strategy, expected_ids", [
    (NoFlaggingStrategy(), []),
    (VulnerableOnlyStrategy(), ["P011"]),
    (AllAtRiskStrategy(), ["P005", "P011"]),
])
def test_strategies_on_sample_data_match_the_expected_results(strategy, expected_ids):
    patients = load_patients(SAMPLE_DATA)

    assert selected_ids(strategy, patients) == expected_ids


def test_base_strategy_cannot_be_created_directly():
    with pytest.raises(TypeError):
        FlaggingStrategy()