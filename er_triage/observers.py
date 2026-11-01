import logging
from dataclasses import dataclass

from .models import Patient

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PatientFlaggedEvent:
    patient: Patient
    heat_level: str


class EventPublisher:
    def __init__(self):
        self.observers = []

    def subscribe(self, observer):
        self.observers.append(observer)

    def publish(self, event):
        for observer in self.observers:
            observer.notify(event)


class AuditLogObserver:
    def __init__(self):
        self.entries = []

    def notify(self, event):
        # Only the patient ID is logged; the name is personal information
        message = (
            f"Patient {event.patient.patient_id} flagged for reassessment "
            f"(heat level: {event.heat_level})"
        )
        logger.info(message)
        self.entries.append(message)


class ReassessmentWorklist:
    def __init__(self):
        self.patients = []
        self.claims = {}

    def notify(self, event):
        if event.patient not in self.patients:
            self.patients.append(event.patient)

    def pending(self):
        # A patient who started treatment is no longer flagged and drops out of the list
        flagged = [patient for patient in self.patients if patient.needs_reassessment]
        return sorted(flagged, key=lambda patient: (patient.assessment.urgency_level, patient.arrival_time))

    def claim_next(self, nurse_id):
        waiting = self.pending()
        if not waiting:
            return None
        patient = waiting[0]
        self.patients.remove(patient)
        self.claims[patient.patient_id] = nurse_id
        return patient