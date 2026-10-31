import json
from datetime import date, datetime, time
from .models import Patient


def to_todays_arrival_time(arrival_clock, line_number):
    # The data file stores only the clock time; the arrival date is always today
    try:
        clock = time.fromisoformat(arrival_clock)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid arrival time on line {line_number}: {arrival_clock!r}") from None
    return datetime.combine(date.today(), clock).isoformat()


def load_patients(file_path):
    patients = []
    patient_ids = set()

    required_fields = {"patient_id","name","age","arrival_time","status","assessment"}

    with open(file_path, encoding="utf-8") as json_file:
        for line_number, line in enumerate(json_file, start=1):
            if not line.strip():
                continue
            try:
                patient_dict = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"Invalid JSON on line {line_number}") from error

            missing_fields = required_fields - patient_dict.keys()

            if missing_fields:
                raise ValueError(f"Missing fields on line {line_number}: {missing_fields}")

            patient_id = patient_dict["patient_id"]

            if patient_id in patient_ids:
                raise ValueError(f"Duplicate patient ID: {patient_id}")

            patient_dict["arrival_time"] = to_todays_arrival_time(patient_dict["arrival_time"], line_number)

            patient = Patient.patient_from_dict(patient_dict)

            patients.append(patient)
            patient_ids.add(patient_id)

    return patients