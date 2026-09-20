from collections import deque
import heapq

def build_patient_lookup(patients):
    patient_lookup = {}
    for patient in patients:
        patient_lookup[patient.patient_id] = patient
    return patient_lookup

def group_patients_by_urgency(patients):
    patient_urgency = {}
    for patient in patients:
        if patient.assessment.urgency_level not in patient_urgency:
            patient_urgency[patient.assessment.urgency_level] = [patient]
        else:
            patient_urgency[patient.assessment.urgency_level].append(patient)
    return patient_urgency

def get_unique_urgency_levels(patients):
    return {patient.assessment.urgency_level for patient in patients}

def get_waiting_patients(patients):
    return [patient for patient in patients if patient.is_waiting]

def get_patient_names(patients):
    return {patient.patient_id: patient.name for patient in patients}

def create_arrival_queue(patients):
    sorted_patients = sorted(patients, key=lambda patient: patient.arrival_time)
    return deque(sorted_patients)

def create_priority_queue(patients):
    priority_queue = []
    for patient in patients:
        patient_tuple = (patient.assessment.urgency_level,patient.arrival_time,patient.patient_id,patient)
        heapq.heappush(priority_queue, patient_tuple)
    return priority_queue

def pop_next_patient(priority_queue):
    if len(priority_queue) == 0:
        return None
    patient_tuple = heapq.heappop(priority_queue)
    patient = patient_tuple[3]
    patient.start_treatment()
    return patient

def get_urgency_level(patient):
    return patient.assessment.urgency_level

def sort_patients_by_urgency(patients):
    sorted_patients = sorted(patients, key=get_urgency_level)
    return sorted_patients

def sort_patients_by_priority(patients):
    sorted_patients = sorted(patients, key=lambda patient: (patient.assessment.urgency_level, patient.arrival_time))
    return sorted_patients

def find_common_patients(first_set,second_set):
     return first_set & second_set

def find_patient_by_id(patient_lookup,patient_id):
    return patient_lookup.get(patient_id)

def get_lookup_entries(patient_lookup):
    return list(patient_lookup.items())

def split_patient_ids(patient_ids):
    first , *rest = patient_ids
    return first, rest

def is_patient_in_set(patient_ids,patient_id):
    return patient_id in patient_ids

def get_patient_id_name_pairs(patient_lookup):
    pairs = []
    for patient_id , patient in patient_lookup.items():
        pairs.append((patient_id , patient.name))
    return pairs

def add_patient_to_arrival_queue(patient,arrival_queue):
    arrival_queue.append(patient)
    return arrival_queue

def pop_next_arrival(arrival_queue):
    if len(arrival_queue) == 0:
        return None
    return arrival_queue.popleft()
