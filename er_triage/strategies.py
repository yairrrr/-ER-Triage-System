from abc import ABC, abstractmethod

# Chosen by the group from common signs of heat-related illness; matched case-insensitively
HEAT_SENSITIVE_KEYWORDS = ("dizz", "weak", "confus", "breath", "fever")
AT_RISK_AGE = 65


def is_heat_sensitive(patient):
    complaint = patient.assessment.chief_complaint.lower()
    return any(keyword in complaint for keyword in HEAT_SENSITIVE_KEYWORDS)


def is_elderly(patient):
    return patient.age >= AT_RISK_AGE


class FlaggingStrategy(ABC):
    """Decides which waiting patients need reassessment at one heat level."""

    def eligible(self, patient):
        # Urgency 1 is already the highest priority, so a reassessment would not change the order
        return (
            patient.is_waiting
            and patient.assessment is not None
            and patient.assessment.urgency_level > 1
            and not patient.needs_reassessment
        )

    @abstractmethod
    def select(self, patients):
        pass


class NoFlaggingStrategy(FlaggingStrategy):
    def select(self, patients):
        return []


class VulnerableOnlyStrategy(FlaggingStrategy):
    def select(self, patients):
        return [
            patient for patient in patients
            if self.eligible(patient) and is_elderly(patient) and is_heat_sensitive(patient)
        ]


class AllAtRiskStrategy(FlaggingStrategy):
    def select(self, patients):
        return [
            patient for patient in patients
            if self.eligible(patient) and (is_elderly(patient) or is_heat_sensitive(patient))
        ]