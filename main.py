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
from er_triage.models import EmergencyQueue, Nurse, Doctor

def main():
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

if __name__ == "__main__":
    main()