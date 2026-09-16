import json
from .models import Patient

def load_patients(file_path):
    patients = []
    with open(file_path) as json_file:
        for line in json_file:
            patient_dict = json.loads(line)
            patient = Patient.patient_from_dict(patient_dict)
            patients.append(patient)
    return patients

