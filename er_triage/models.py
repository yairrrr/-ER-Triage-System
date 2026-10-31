from abc import ABC, abstractmethod
from datetime import date, datetime
from dataclasses import dataclass

def is_whole_number(value):
    # bool is a subclass of int, so True/False must be rejected explicitly
    return isinstance(value, int) and not isinstance(value, bool)


class TriageAssessment:
    def __init__(self,chief_complaint,pain_level,urgency_level):
        self.chief_complaint = chief_complaint
        self.pain_level = pain_level
        self.urgency_level = urgency_level

    def __str__(self):
        return (
            f"Urgency {self.urgency_level} - "
            f"{self.chief_complaint}"
        )

    def __repr__(self):
        return (
            f"TriageAssessment("
            f"chief_complaint={self.chief_complaint!r}, "
            f"pain_level={self.pain_level!r}, "
            f"urgency_level={self.urgency_level!r})"
        )

    @property
    def pain_level(self):
        return self._pain_level

    @pain_level.setter
    def pain_level(self, pain_level):
        if is_whole_number(pain_level) and 0 <= pain_level <= 10:
            self._pain_level = pain_level
        else:
            raise ValueError("Pain level must be a whole number between 0 and 10")

    @property
    def urgency_level(self):
        return self._urgency_level

    @urgency_level.setter
    def urgency_level(self, urgency_level):
        if self.is_valid_urgency(urgency_level):
            self._urgency_level = urgency_level
        else:
            raise ValueError("Urgency level must be a whole number between 1 and 5")

    @staticmethod
    def is_valid_urgency(urgency_level):
        return is_whole_number(urgency_level) and 1 <= urgency_level <= 5

    @classmethod
    def from_dict(cls, data_dict):
        return cls(data_dict["chief_complaint"],data_dict["pain_level"],data_dict["urgency_level"])

class Patient:
    def __init__(self,patient_id , name , age , arrival_time , assessment=None , status = "waiting"):
        self.name = name
        self.patient_id = patient_id
        self.age = age
        self.arrival_time = arrival_time
        self.status = status
        self.assessment = assessment
        self.needs_reassessment = False
        self.reassessment_reason = None

    def __str__(self):
        return f"{self.name} ({self.patient_id})"

    def __repr__(self):
        return (
            f"Patient(patient_id={self.patient_id!r}, "
            f"name={self.name!r}, "
            f"age={self.age!r}, "
            f"status={self.status!r})"
        )

    @property
    def status(self):
        return self._status
    @status.setter
    def status(self, status):
        if status not in ("waiting", "in_treatment", "completed"):
            raise ValueError("Invalid patient status")
        self._status = status

    @property
    def age(self):
        return self._age
    @age.setter
    def age(self, age):
        if not is_whole_number(age) or age < 0 or age > 120:
            raise ValueError("Age must be a whole number between 0 and 120")
        else:
            self._age = age

    @property
    def arrival_time(self):
        return self._arrival_time
    @arrival_time.setter
    def arrival_time(self, arrival_time):
        if not isinstance(arrival_time, str):
            raise ValueError("Arrival time must be an ISO date-time string")
        try:
            parsed_time = datetime.fromisoformat(arrival_time)
        except ValueError:
            raise ValueError(f"Invalid arrival time: {arrival_time!r}") from None
        if parsed_time.date() != date.today():
            raise ValueError(f"Arrival time must be today: {arrival_time!r}")
        # Stored in one normalized format so string comparison keeps chronological order
        self._arrival_time = parsed_time.isoformat()

    @property
    def is_waiting(self):
        if self.status == "waiting":
            return True
        else:
            return False

    def __eq__(self, other):
        if isinstance(other,Patient):
            return self.patient_id == other.patient_id
        return False

    def __lt__(self, other):
        if not isinstance(other, Patient):
            return NotImplemented
        return (self.assessment.urgency_level,self.arrival_time) < (other.assessment.urgency_level,other.arrival_time)

    @classmethod
    def patient_from_dict(cls,data_dict):
        patient_id = data_dict["patient_id"]
        name = data_dict["name"]
        age = data_dict["age"]
        arrival_time = data_dict["arrival_time"]
        assessment = data_dict.get("assessment", None)
        status = data_dict.get("status", "waiting")
        if assessment is not None:
            assessment = TriageAssessment.from_dict(assessment)
        return cls(patient_id,name,age,arrival_time,assessment,status)

    def flag_for_reassessment(self, reason):
        if not self.is_waiting:
            raise ValueError(
                f"Only a waiting patient can be flagged for reassessment, "
                f"patient {self.patient_id} is {self.status}"
            )
        self.needs_reassessment = True
        self.reassessment_reason = reason

    def start_treatment(self):
        self.status = "in_treatment"
        self.needs_reassessment = False
        self.reassessment_reason = None

    def complete_treatment(self):
        self.status = "completed"


class MedicalStaff(ABC):
    def __init__(self,staff_id,name,department="ER"):
        self.staff_id = staff_id
        self.name = name
        self.department = department
    @abstractmethod
    def get_role(self):
        pass

    def __str__(self):
        return f"{self.name} - {self.get_role()}"

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"staff_id={self.staff_id!r}, "
            f"name={self.name!r}, "
            f"department={self.department!r})"
        )

class Nurse(MedicalStaff):
    def get_role(self):
        return "Nurse"

class Doctor(MedicalStaff):
    def get_role(self):
        return "Doctor"

class EmergencyQueue:
    def __init__(self):
        self.patients = []

    def add_patient(self,patient):
        if patient.assessment is None:
            raise ValueError("Patient must have assessment")
        if patient in self.patients:
            raise ValueError(f"Patient {patient.patient_id} is already in the queue")
        self.patients.append(patient)
        self.sort_queue()

    def remove_patient(self,patient):
        self.patients.remove(patient)

    def __len__(self):
        return len(self.patients)

    def update_patient_urgency(self,patient,new_urgency_level):
        if patient.assessment is None:
            raise ValueError("Patient must have assessment")
        patient.assessment.urgency_level = new_urgency_level
        self.sort_queue()

    def sort_queue(self):
        self.patients.sort(key=lambda patient: (patient.assessment.urgency_level,patient.arrival_time))

    def get_next_patient(self):
        if len(self.patients) == 0:
            return None
        next_patient = self.patients.pop(0)
        next_patient.start_treatment()
        return next_patient

    def print_queue(self):
        for patient in self.patients:
            print(
                patient.name,
                patient.assessment.urgency_level,
                patient.arrival_time
            )

    def __str__(self):
        return f"Emergency Queue ({len(self.patients)} patients)"

    def __repr__(self):
        return f"EmergencyQueue(patients={self.patients!r})"

@dataclass(frozen=True)
class HourlyForecast:
    time: str
    apparent_temperature_c: float


@dataclass(frozen=True)
class WeatherSnapshot:
    observed_at: str
    temperature_c: float
    apparent_temperature_c: float
    humidity_percent: float
    forecast: tuple[HourlyForecast, ...]
    source: str
