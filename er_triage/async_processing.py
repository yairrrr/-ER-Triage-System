import asyncio
import json
from dataclasses import dataclass

# Simulated waiting time when no delay is given for a patient
DEFAULT_DELAY_SECONDS = 0.1


@dataclass(frozen=True)
class LabResult:
    patient_id: str
    test_name: str
    value: float
    is_critical: bool


def load_lab_data(file_path):
    with open(file_path, encoding="utf-8") as lab_file:
        return json.load(lab_file)


async def fetch_lab_result(patient_id, lab_data, delays):
    # Simulates waiting for the lab system; no real network call is made
    await asyncio.sleep(delays.get(patient_id, DEFAULT_DELAY_SECONDS))
    if patient_id not in lab_data:
        raise KeyError(f"No lab result for patient {patient_id}")
    record = lab_data[patient_id]
    return LabResult(patient_id, record["test_name"], float(record["value"]), bool(record["is_critical"]))


async def collect_lab_results_sequential(patient_ids, lab_data, delays):
    results = []
    for patient_id in patient_ids:
        result = await fetch_lab_result(patient_id, lab_data, delays)
        results.append(result)
    return results


async def collect_lab_results_concurrent(patient_ids, lab_data, delays):
    requests = [fetch_lab_result(patient_id, lab_data, delays) for patient_id in patient_ids]
    results = await asyncio.gather(*requests)
    return list(results)


def find_critical_patients(results):
    return [result.patient_id for result in results if result.is_critical]