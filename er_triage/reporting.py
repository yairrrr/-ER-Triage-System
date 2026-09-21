from datetime import datetime

def generate_waiting_report(patients):
    waiting_patients = [patient for patient in patients if patient.is_waiting]
    total_waiting = len(waiting_patients)
    current_time = datetime.now()
    waiting_times = []
    for patient in waiting_patients:
        arrival_time = datetime.fromisoformat(patient.arrival_time)
        waiting_time = current_time - arrival_time
        waiting_minutes = waiting_time.total_seconds() / 60
        waiting_times.append(waiting_minutes)
    if waiting_times:
        average_waiting_time = sum(waiting_times) / len(waiting_times)
        longest_waiting_time = max(waiting_times)
    else:
        average_waiting_time = 0
        longest_waiting_time = 0
    report = {
        "total_waiting": total_waiting,
        "average_waiting_time": round(average_waiting_time,2),
        "longest_waiting_time": round(longest_waiting_time,2),
        "waiting_patients": [
            {
                "patient_id": patient.patient_id,
                "name": patient.name,
                "urgency_level": patient.assessment.urgency_level,
                "arrival_time": patient.arrival_time
            }
            for patient in waiting_patients
        ]
            }
    return report

