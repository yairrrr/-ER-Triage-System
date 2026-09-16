from abc import ABC, abstractmethod
class TriageAssessment:
    def __init__(self,chief_complaint,pain_level,urgency_level):
        self.chief_complaint = chief_complaint
        self.pain_level = pain_level
        self.urgency_level = urgency_level

    @property
    def pain_level(self):
        return self._pain_level

    @pain_level.setter
    def pain_level(self, pain_level):
        if 0 <= pain_level <= 10:
            self._pain_level = pain_level
        else:
            raise ValueError("Pain level must be between 0 and 10")

    @property
    def urgency_level(self):
        return self._urgency_level

    @urgency_level.setter
    def urgency_level(self, urgency_level):
        if 1 <= urgency_level <= 5:
            self._urgency_level = urgency_level
        else:
            raise ValueError("Urgency level must be between 1 and 5")

class Patient:
    def __init__(self,patient_id , name , age , arrival_time , assessment=None , status = "waiting"):
        self.name = name
        self.patient_id = patient_id
        self.age = age
        self.arrival_time = arrival_time
        self.status = status
        self.assessment = assessment

    @property
    def age(self):
        return self._age
    @age.setter
    def age(self, age):
        if age < 0 or age > 120:
            raise ValueError("Age must be between 0 and 120")
        else:
            self._age = age

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

    @classmethod
    def patient_from_dict(cls,data_dict):
        patient_id = data_dict["patient_id"]
        name = data_dict["name"]
        age = data_dict["age"]
        arrival_time = data_dict["arrival_time"]
        assessment = data_dict.get("assessment", None)
        status = data_dict.get("status", "waiting")
        if assessment is not None:
            chief_complaint = data_dict["assessment"]["chief_complaint"]
            pain_level = data_dict["assessment"]["pain_level"]
            urgency_level = data_dict["assessment"]["urgency_level"]
            return cls(patient_id , name , age , arrival_time , TriageAssessment(chief_complaint,pain_level,urgency_level) , status )
        return cls(patient_id,name,age,arrival_time,assessment,status)


class MedicalStaff(ABC):
    def __init__(self,staff_id,name,department="ER"):
        self.staff_id = staff_id
        self.name = name
        self.department = department
    @abstractmethod
    def get_role(self):
        pass

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
        self.patients.append(patient)

    def remove_patient(self,patient):
        self.patients.remove(patient)

    def __len__(self):
        return len(self.patients)
