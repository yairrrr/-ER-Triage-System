import logging

from er_triage.observers import (
    AuditLogObserver,
    EventPublisher,
    PatientFlaggedEvent,
    ReassessmentWorklist,
)
from tests.conftest import make_patient, today_at


def flag_and_publish(publisher, patient, heat_level="danger"):
    patient.flag_for_reassessment(f"heat:{heat_level}")
    publisher.publish(PatientFlaggedEvent(patient, heat_level))


def test_one_event_reaches_both_observers():
    publisher = EventPublisher()
    audit_log = AuditLogObserver()
    worklist = ReassessmentWorklist()
    publisher.subscribe(audit_log)
    publisher.subscribe(worklist)
    patient = make_patient("O001", 72, "Dizziness", 3)

    flag_and_publish(publisher, patient)

    assert audit_log.entries == ["Patient O001 flagged for reassessment (heat level: danger)"]
    assert worklist.pending() == [patient]


def test_observers_are_notified_in_subscription_order():
    calls = []

    class RecordingObserver:
        def __init__(self, name):
            self.name = name

        def notify(self, event):
            calls.append(self.name)

    publisher = EventPublisher()
    publisher.subscribe(RecordingObserver("first"))
    publisher.subscribe(RecordingObserver("second"))

    flag_and_publish(publisher, make_patient("O001", 72, "Dizziness", 3))

    assert calls == ["first", "second"]


def test_publish_without_observers_does_nothing():
    EventPublisher().publish(PatientFlaggedEvent(make_patient("O001", 72, "Dizziness", 3), "danger"))


def test_audit_log_writes_patient_id_and_not_name(caplog):
    publisher = EventPublisher()
    publisher.subscribe(AuditLogObserver())
    patient = make_patient("O001", 72, "Dizziness", 3)

    with caplog.at_level(logging.INFO, logger="er_triage.observers"):
        flag_and_publish(publisher, patient)

    assert "O001" in caplog.text
    assert patient.name not in caplog.text


def test_pending_is_ordered_by_urgency_then_arrival():
    publisher = EventPublisher()
    worklist = ReassessmentWorklist()
    publisher.subscribe(worklist)
    later_urgent = make_patient("O001", 72, "Dizziness", 2, arrival_time=today_at(6, 30))
    earlier_less_urgent = make_patient("O002", 70, "Weakness", 3, arrival_time=today_at(6, 0))
    later_less_urgent = make_patient("O003", 68, "Fever", 3, arrival_time=today_at(6, 45))

    for patient in (later_less_urgent, earlier_less_urgent, later_urgent):
        flag_and_publish(publisher, patient)

    assert [patient.patient_id for patient in worklist.pending()] == ["O001", "O002", "O003"]


def test_patient_who_started_treatment_leaves_the_worklist():
    publisher = EventPublisher()
    worklist = ReassessmentWorklist()
    publisher.subscribe(worklist)
    patient = make_patient("O001", 72, "Dizziness", 3)
    flag_and_publish(publisher, patient)

    patient.start_treatment()

    assert worklist.pending() == []


def test_same_patient_is_added_only_once():
    worklist = ReassessmentWorklist()
    patient = make_patient("O001", 72, "Dizziness", 3)
    patient.flag_for_reassessment("heat:danger")
    event = PatientFlaggedEvent(patient, "danger")

    worklist.notify(event)
    worklist.notify(event)

    assert worklist.pending() == [patient]


def test_claim_next_returns_first_patient_and_records_the_nurse():
    publisher = EventPublisher()
    worklist = ReassessmentWorklist()
    publisher.subscribe(worklist)
    first = make_patient("O001", 72, "Dizziness", 2)
    second = make_patient("O002", 70, "Weakness", 3)
    flag_and_publish(publisher, first)
    flag_and_publish(publisher, second)

    claimed = worklist.claim_next("N1")

    assert claimed is first
    assert worklist.claims == {"O001": "N1"}
    assert worklist.pending() == [second]


def test_claim_next_on_empty_worklist_returns_none():
    assert ReassessmentWorklist().claim_next("N1") is None