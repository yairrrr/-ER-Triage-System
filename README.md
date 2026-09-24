# ER Triage System

A system for managing and prioritizing patients in a hospital emergency room.

## Project Proposal

ER Triage System is a local Python system designed to help emergency room staff manage and prioritize patients according to medical urgency and arrival time.

### Business Need

Emergency departments need to manage multiple waiting patients while ensuring that urgent cases receive priority. A simple arrival-order queue is not sufficient because a patient who arrives later may require more urgent treatment.

The system provides a structured queue that reflects the urgency level assigned by the triage staff and updates automatically when a patient's condition changes.

### Main Users

- **Triage Nurse** – registers patients, records the triage assessment, assigns an urgency level, and may update the urgency level while the patient is waiting.
- **Doctor** – receives the next patient selected for treatment.
- **Emergency Department Manager** – can use system information and reports to understand the current waiting-room situation.

### Main Business Process

A new patient is registered together with basic information.

The triage nurse performs an assessment and assigns an urgency level from 1 to 5:

- `1` – highest urgency
- `5` – lowest urgency

The patient enters the emergency queue.

Patients are prioritized first by urgency level and then by arrival time when the urgency level is equal.

If a patient's condition changes while waiting, the triage nurse can update the urgency level and the system updates the patient's position in the queue.

When a patient is selected for treatment, the status changes from:

`waiting → in_treatment`

When treatment is completed:

`in_treatment → completed`

### Information Flow

The system receives:

- Patient ID
- Patient name
- Age
- Arrival time
- Patient status
- Chief complaint
- Pain level
- Urgency level

The medical staff creates and updates this information.

The system uses the information to maintain the patient queue and generate an on-demand waiting-patient report.

### Business Value

The system helps:

- Give priority to urgent cases.
- Maintain a clear and consistent patient queue.
- Reduce manual queue-management errors.
- Reflect changes in patient urgency.
- Provide medical staff with a clear overview of waiting patients.
- Provide basic waiting-time information when requested.

The system supports decisions made by medical staff and does not independently determine medical urgency.

### Main Entities

- `Patient` – represents a patient in the emergency department.
- `TriageAssessment` – represents the patient's triage assessment and urgency level.
- `EmergencyQueue` – manages patients waiting for treatment.
- `MedicalStaff` – common base class for medical staff.
- `Nurse` – medical staff member responsible for nursing duties.
- `Doctor` – medical staff member responsible for doctor duties.

### Main Use Cases

1. Register a new patient, assign an urgency level, and add the patient to the appropriate position in the queue.
2. Select the next patient for treatment according to urgency level and arrival time.
3. Update the urgency level of a waiting patient and automatically reposition the patient.
4. Move a patient through the statuses `waiting`, `in_treatment`, and `completed`.
5. Generate an on-demand report about waiting patients and waiting times.

### Future Extension

Future stages may add an external service, automated tests, and concurrency according to later course requirements.

The current system is designed so that these capabilities can be added without replacing the existing business model.

---

## Object-Oriented Design

### Composition

The system uses composition between `Patient` and `TriageAssessment`.

A `Patient` may contain a `TriageAssessment` object that stores:

- Chief complaint
- Pain level
- Urgency level

This represents a real "has-a" relationship: a patient has a triage assessment.

`EmergencyQueue` also manages a collection of `Patient` objects and provides operations for adding patients, removing patients, updating urgency, and selecting the next patient for treatment.

### Inheritance and Polymorphism

`MedicalStaff` is the common base class for medical staff.

The system contains two subclasses:

- `Nurse`
- `Doctor`

Both override the `get_role()` method.

Objects of both types can be stored in the same collection and handled through the same method:

```python
staff_members = [
    Nurse("S001", "Dana"),
    Doctor("S002", "David")
]

for staff_member in staff_members:
    print(staff_member.get_role())