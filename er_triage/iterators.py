

class WaitingPatientIterator:
    def __init__(self, patients):
        self.patients = patients
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        while self.index < len(self.patients):
            patient = self.patients[self.index]
            self.index += 1

            if patient.is_waiting:
                return patient
        raise StopIteration
