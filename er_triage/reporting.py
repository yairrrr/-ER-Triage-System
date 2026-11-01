from datetime import datetime
from .services import summarize_forecast

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

def generate_heat_report(patients, result):
    flagged_patients = [patient for patient in patients if patient.is_waiting and patient.needs_reassessment]
    report = {
        "data_source": "unavailable",
        "status": result.status,
        "heat_level": result.heat_level,
        "observed_at": None,
        "apparent_temperature_c": None,
        "forecast_max_c": None,
        "forecast_max_time": None,
        "forecast_level": None,
        "flagged_count": len(flagged_patients),
        "flagged_patient_ids": [patient.patient_id for patient in flagged_patients],
        "error_message": result.error_message,
    }
    if result.snapshot is not None:
        forecast = summarize_forecast(result.snapshot.forecast)
        report["data_source"] = result.snapshot.source
        report["observed_at"] = result.snapshot.observed_at
        report["apparent_temperature_c"] = result.snapshot.apparent_temperature_c
        report["forecast_max_c"] = forecast["max_apparent_temperature_c"]
        report["forecast_max_time"] = forecast["time"]
        report["forecast_level"] = forecast["expected_level"]
    return report