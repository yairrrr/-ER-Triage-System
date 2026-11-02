import argparse
import asyncio
import logging
import time

import requests

from er_triage import config
from er_triage.api_client import OfflineWeatherClient, OpenMeteoClient, WeatherConnectionError
from er_triage.async_processing import (
    collect_lab_results_concurrent, collect_lab_results_sequential,
    find_critical_patients, load_lab_data,
)
from er_triage.observers import AuditLogObserver, EventPublisher, ReassessmentWorklist
from er_triage.reporting import generate_heat_report
from er_triage.services import HeatAlertService
from er_triage.strategies import AllAtRiskStrategy, NoFlaggingStrategy, VulnerableOnlyStrategy
from er_triage.threaded_processing import nurses_claim_concurrently
from er_triage.repository import load_patients
from er_triage.iterators import WaitingPatients
from er_triage.reporting import generate_waiting_report
from er_triage.context_managers import TriageSession
from er_triage.processing import create_arrival_queue, pop_next_arrival
from er_triage.processing import create_priority_queue, pop_next_patient
from er_triage.processing import build_patient_lookup, find_patient_by_id
from er_triage.processing import get_unique_urgency_levels
from er_triage.processing import group_patients_by_urgency
from er_triage.processing import sort_patients_by_urgency, sort_patients_by_priority
from er_triage.generators import waiting_patients_generator, urgent_waiting_pipeline
from er_triage.models import EmergencyQueue, Nurse, Doctor, Patient, TriageAssessment

def run_stage1_demo():
    patients = load_patients("data/sample_data.jsonl")

    # Emergency Queue
    queue = EmergencyQueue()

    for patient in patients:
        queue.add_patient(patient)

    print("=== Initial Queue ===")
    queue.print_queue()

    # Update urgency
    patient_to_update = patients[-1]
    queue.update_patient_urgency(patient_to_update, 1)

    print("\n=== Queue After Urgency Update ===")
    queue.print_queue()

    # Patient treatment status
    next_patient = queue.get_next_patient()

    print("\n=== Patient Started Treatment ===")
    print(next_patient.name, next_patient.status)

    next_patient.complete_treatment()

    print("\n=== Patient Completed Treatment ===")
    print(next_patient.name, next_patient.status)

    # Two independent iterators
    print("\n=== Independent Iterators ===")

    waiting_patients = WaitingPatients(patients)

    iterator_one = iter(waiting_patients)
    iterator_two = iter(waiting_patients)

    first_from_one = next(iterator_one)
    first_from_two = next(iterator_two)
    second_from_one = next(iterator_one)

    print("Iterator one:", first_from_one.name)
    print("Iterator two:", first_from_two.name)
    print("Iterator one again:", second_from_one.name)

    print("\n=== Generator ===")

    waiting_generator = waiting_patients_generator(patients)

    first_generated = next(waiting_generator)
    print("First:", first_generated.name)

    for patient in waiting_generator:
        print("Next:", patient.name)

    print("Generator finished")

    waiting_generator = waiting_patients_generator(patients)
    print("New generator:", next(waiting_generator).name)

    # Generator Pipeline
    print("\n=== Generator Pipeline ===")

    urgent_waiting = urgent_waiting_pipeline(patients, 1)
    print(next(urgent_waiting))
    print(next(urgent_waiting))

    # Context Manager + Report
    print("\n=== Waiting Report ===")

    with TriageSession("Yair") as session:
        report = generate_waiting_report(patients)

    print(report)
    print("Session duration:", session.duration)

    # deque
    print("\n=== Arrival Queue (deque) ===")

    arrival_queue = create_arrival_queue(patients)
    first_arrival = pop_next_arrival(arrival_queue)

    print(first_arrival.name, first_arrival.arrival_time)

    # heapq
    print("\n=== Priority Queue (heapq) ===")

    priority_queue = create_priority_queue(patients)
    next_priority_patient = pop_next_patient(priority_queue)

    print(
        next_priority_patient.name,
        next_priority_patient.assessment.urgency_level
    )

    # Dictionary lookup
    print("\n=== Patient Lookup ===")

    patient_lookup = build_patient_lookup(patients)
    found_patient = find_patient_by_id(patient_lookup, "P001")

    print(found_patient.name)

    # Set
    print("\n=== Unique Urgency Levels ===")

    urgency_levels = get_unique_urgency_levels(patients)
    print(urgency_levels)

    # Dictionary grouping + items unpacking
    print("\n=== Patients Grouped By Urgency ===")

    grouped_patients = group_patients_by_urgency(patients)

    for urgency_level, group in grouped_patients.items():
        print(urgency_level, len(group))

    # Sorting
    print("\n=== Sorting ===")

    sorted_by_urgency = sort_patients_by_urgency(patients)
    sorted_by_priority = sort_patients_by_priority(patients)

    print(
        "By urgency:",
        sorted_by_urgency[0].name,
        sorted_by_urgency[0].assessment.urgency_level
    )

    print(
        "By priority:",
        sorted_by_priority[0].name,
        sorted_by_priority[0].assessment.urgency_level,
        sorted_by_priority[0].arrival_time
    )
    print("\n=== OOP Special Methods ===")

    print("Queue length:", len(queue))

    print(
        "Patient comparison:",
        patients[0] < patients[1]
    )

    print(
        "Patient equality:",
        patients[0] == patients[0]
    )

    print("\n=== Validation ===")

    try:
        Patient("P100", "Test Patient", 30, "not-a-date", TriageAssessment("Headache", 3, 4))
    except ValueError as error:
        print("Arrival time check:", error)

    try:
        Patient("P101", "Test Patient", 30, "2020-01-01T10:00:00", TriageAssessment("Headache", 3, 4))
    except ValueError as error:
        print("Arrival date check:", error)

    try:
        TriageAssessment("Headache", 3, 2.5)
    except ValueError as error:
        print("Urgency level check:", error)

    validation_queue = EmergencyQueue()
    validation_queue.add_patient(patients[1])

    try:
        validation_queue.add_patient(patients[1])
    except ValueError as error:
        print("Duplicate patient check:", error)

    print("\n=== Polymorphism ===")

    staff_members = [
        Nurse("S001", "Dana"),
        Doctor("S002", "David")
    ]

    for staff_member in staff_members:
        print(staff_member.get_role())

    # Context Manager with exception
    print("\n=== Context Manager Exception ===")

    try:
        with TriageSession("Yair") as error_session:
            raise ValueError("Demo error inside triage session")
    except ValueError as error:
        print("Caught error:", error)

    print("Error session duration:", error_session.duration)

class FailingWeatherClient:
    def get_weather(self):
        raise WeatherConnectionError("Simulated weather connection failure")


def build_heat_service(weather_client):
    publisher = EventPublisher()
    audit_log = AuditLogObserver()
    worklist = ReassessmentWorklist()
    publisher.subscribe(audit_log)
    publisher.subscribe(worklist)
    strategies = {
        "normal": NoFlaggingStrategy(),
        "caution": VulnerableOnlyStrategy(),
        "danger": AllAtRiskStrategy(),
    }
    return HeatAlertService(weather_client, publisher, strategies), audit_log, worklist


def display_heat_check(patients, service, audit_log, worklist):
    result = service.run_check(patients)
    print("Heat level:", result.heat_level)
    print("Flagged patient IDs:", result.flagged_patient_ids)
    for patient in patients:
        if patient.needs_reassessment:
            print(patient.patient_id, patient.reassessment_reason)
    print("Audit log:", audit_log.entries)
    print("Nurse worklist:", [patient.patient_id for patient in worklist.pending()])
    print("Heat report:", generate_heat_report(patients, result))


def run_stage2_demo(live):
    print("\n=== Stage 2: Heat Alert ===")
    patients = load_patients("data/sample_data.jsonl")
    if live:
        print("[DATA SOURCE: LIVE – Open-Meteo]")
        with requests.Session() as session:
            weather_client = OpenMeteoClient(
                session, base_url=config.WEATHER_API_URL,
                latitude=config.HOSPITAL_LATITUDE, longitude=config.HOSPITAL_LONGITUDE,
                timeout=config.WEATHER_TIMEOUT_SECONDS,
                forecast_hours=config.WEATHER_FORECAST_HOURS,
                max_attempts=config.WEATHER_MAX_ATTEMPTS, base_delay=config.WEATHER_BASE_DELAY,
            )
            service, audit_log, worklist = build_heat_service(weather_client)
            display_heat_check(patients, service, audit_log, worklist)
    else:
        print(f"[DATA SOURCE: SIMULATED – {config.WEATHER_SAMPLE_FILE}]")
        service, audit_log, worklist = build_heat_service(
            OfflineWeatherClient(config.WEATHER_SAMPLE_FILE)
        )
        display_heat_check(patients, service, audit_log, worklist)

    print("\n=== Weather Failure [SIMULATED] ===")
    failure_patients = load_patients("data/sample_data.jsonl")
    failure_service, failure_audit, failure_worklist = build_heat_service(FailingWeatherClient())
    display_heat_check(failure_patients, failure_service, failure_audit, failure_worklist)

    print("\n=== Lab Results [SIMULATED] ===")
    lab_data = load_lab_data("data/lab_results.json")
    patient_ids = [patient.patient_id for patient in patients if patient.patient_id in lab_data]
    delays = {patient_id: 0.1 for patient_id in patient_ids}
    start = time.perf_counter()
    sequential = asyncio.run(collect_lab_results_sequential(patient_ids, lab_data, delays))
    sequential_time = time.perf_counter() - start
    start = time.perf_counter()
    concurrent = asyncio.run(collect_lab_results_concurrent(patient_ids, lab_data, delays))
    concurrent_time = time.perf_counter() - start
    print("Sequential results:", sequential)
    print("Sequential seconds:", round(sequential_time, 3))
    print("Concurrent results:", concurrent)
    print("Concurrent seconds:", round(concurrent_time, 3))
    print("Critical patient IDs:", find_critical_patients(concurrent))

    print("\n=== Nurse Claims [SIMULATED] ===")
    if not worklist.pending():
        print("No patients in the nurse worklist; the Threads demo made no actual claims.")
    print("Claimed patient IDs:", nurses_claim_concurrently(worklist, ["N1", "N2", "N3"]))
    print("Remaining worklist:", [patient.patient_id for patient in worklist.pending()])


def main():
    parser = argparse.ArgumentParser(description="ER triage demonstrations")
    parser.add_argument("--live", action="store_true", help="Use live Open-Meteo weather data")
    args = parser.parse_args()
    logging.basicConfig(level=config.LOG_LEVEL)
    run_stage1_demo()
    run_stage2_demo(args.live)


if __name__ == "__main__":
    main()
