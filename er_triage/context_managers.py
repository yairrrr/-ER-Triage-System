from datetime import datetime

class TriageSession:
    def __init__(self,staff_name):
        self.staff_name = staff_name
        self.start_time = None
        self.end_time = None
        self.duration = None

    def __enter__(self):
        self.start_time = datetime.now()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = datetime.now()
        self.duration = self.end_time - self.start_time
        return False


