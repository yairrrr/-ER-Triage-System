import json
from datetime import date

import pytest

from er_triage.repository import load_patients


def patient_record(patient_id, arrival_time="06:00:00"):
    return {
        "patient_id": patient_id,
        "name": f"Test {patient_id}",
        "age": 40,
        "arrival_time": arrival_time,
        "status": "waiting",
        "assessment": {"chief_complaint": "Headache", "pain_level": 3, "urgency_level": 4},
    }


def write_jsonl(tmp_path, lines):
    file_path = tmp_path / "patients.jsonl"
    file_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return file_path


def test_valid_file_loads_patients_with_todays_arrival_date(tmp_path):
    file_path = write_jsonl(tmp_path, [
        json.dumps(patient_record("R001", "06:00:00")),
        json.dumps(patient_record("R002", "06:30:00")),
    ])

    patients = load_patients(file_path)

    assert [patient.patient_id for patient in patients] == ["R001", "R002"]
    assert patients[1].arrival_time == f"{date.today().isoformat()}T06:30:00"


def test_invalid_clock_time_raises_value_error_with_line_number(tmp_path):
    file_path = write_jsonl(tmp_path, [
        json.dumps(patient_record("R001")),
        json.dumps(patient_record("R002", "25:00:00")),
    ])

    with pytest.raises(ValueError, match="line 2"):
        load_patients(file_path)


def test_broken_json_line_raises_value_error_with_line_number(tmp_path):
    file_path = write_jsonl(tmp_path, [
        json.dumps(patient_record("R001")),
        '{"patient_id": "R002", "name":',
    ])

    with pytest.raises(ValueError, match="Invalid JSON on line 2"):
        load_patients(file_path)


def test_missing_field_raises_value_error(tmp_path):
    record = patient_record("R001")
    del record["age"]
    file_path = write_jsonl(tmp_path, [json.dumps(record)])

    with pytest.raises(ValueError, match="Missing fields on line 1"):
        load_patients(file_path)


def test_duplicate_patient_id_raises_value_error(tmp_path):
    file_path = write_jsonl(tmp_path, [
        json.dumps(patient_record("R001")),
        json.dumps(patient_record("R001")),
    ])

    with pytest.raises(ValueError, match="Duplicate patient ID: R001"):
        load_patients(file_path)