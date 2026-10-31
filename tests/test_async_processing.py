import asyncio
import json
import time

import pytest

from er_triage.async_processing import (
    LabResult,
    collect_lab_results_concurrent,
    collect_lab_results_sequential,
    fetch_lab_result,
    find_critical_patients,
    load_lab_data,
)

LAB_DATA = {
    "A001": {"test_name": "Troponin", "value": 1.2, "is_critical": True},
    "A002": {"test_name": "Glucose", "value": 95.0, "is_critical": False},
    "A003": {"test_name": "Potassium", "value": 2.5, "is_critical": True},
}
PATIENT_IDS = ["A001", "A002", "A003"]
# The first patient waits the longest, so the finishing order (A002, A003, A001) differs from the input order
DELAYS = {"A001": 0.15, "A002": 0.05, "A003": 0.10}


def test_sequential_and_concurrent_versions_return_the_same_results():
    sequential = asyncio.run(collect_lab_results_sequential(PATIENT_IDS, LAB_DATA, DELAYS))
    concurrent = asyncio.run(collect_lab_results_concurrent(PATIENT_IDS, LAB_DATA, DELAYS))

    assert sequential == concurrent


def test_concurrent_results_follow_input_order_even_when_finishing_order_differs():
    results = asyncio.run(collect_lab_results_concurrent(PATIENT_IDS, LAB_DATA, DELAYS))

    assert [result.patient_id for result in results] == ["A001", "A002", "A003"]
    assert results[0] == LabResult("A001", "Troponin", 1.2, True)


def test_concurrent_version_overlaps_the_waiting_time():
    start = time.perf_counter()
    asyncio.run(collect_lab_results_sequential(PATIENT_IDS, LAB_DATA, DELAYS))
    sequential_time = time.perf_counter() - start

    start = time.perf_counter()
    asyncio.run(collect_lab_results_concurrent(PATIENT_IDS, LAB_DATA, DELAYS))
    concurrent_time = time.perf_counter() - start

    # Total waiting is 0.30 s; overlapped waiting is about 0.15 s (the longest single delay)
    assert sequential_time >= 0.29
    assert concurrent_time < 0.25


def test_find_critical_patients_returns_only_critical_ids():
    results = asyncio.run(collect_lab_results_concurrent(PATIENT_IDS, LAB_DATA, DELAYS))

    assert find_critical_patients(results) == ["A001", "A003"]


def test_missing_patient_raises_key_error():
    with pytest.raises(KeyError, match="A999"):
        asyncio.run(fetch_lab_result("A999", LAB_DATA, {"A999": 0}))


def test_load_lab_data_reads_json_file(tmp_path):
    lab_file = tmp_path / "lab_results.json"
    lab_file.write_text(json.dumps(LAB_DATA), encoding="utf-8")

    assert load_lab_data(lab_file) == LAB_DATA