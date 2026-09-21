

def waiting_patients_generator(patients):
    for patient in patients:
        if patient.is_waiting:
            yield patient

def urgency_filter_generator(patients, urgency_level):
    for patient in patients:
        if patient.assessment.urgency_level == urgency_level:
            yield patient

def urgent_waiting_pipeline(patients, urgency_level):
    waiting = waiting_patients_generator(patients)
    return urgency_filter_generator(waiting, urgency_level)
