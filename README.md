# ER Triage System

A system for managing and prioritizing patients in a hospital emergency room.

## Project Proposal

The system is designed to help emergency room staff manage the patient queue according to urgency level and arrival time.

A new patient is registered in the system together with initial information about their condition. The triage nurse assigns an urgency level from 1 to 5, and the system places the patient in the appropriate position in the queue.

If the patient's condition changes while waiting, the triage nurse can update the urgency level and the system updates the patient's position in the queue accordingly.

The system also manages the patient's status throughout the process:

- `waiting`
- `in_treatment`
- `completed`

An on-demand function will provide a basic report about waiting patients and their waiting times.

The purpose of the system is to give priority to urgent cases, improve queue management, and provide the medical staff with a clear overview of the patients currently waiting.

The system supports the decisions made by the medical staff and does not determine medical urgency independently.

### Main Users

- Triage Nurse
- Doctor
- Emergency Department Manager

### Main Entities

- `Patient` – Patient
- `TriageAssessment` – Triage assessment and assigned urgency level
- `EmergencyQueue` – Emergency room priority queue
- `MedicalStaff` – Medical staff member

### Main Use Cases

1. Registering a new patient, assigning an urgency level, and placing the patient in the appropriate position in the queue.
2. Selecting the next patient for treatment according to urgency level and arrival time.
3. Updating the urgency level of a waiting patient and repositioning the patient in the queue.
4. Updating patient status from waiting to treatment and then to completed.
5. Generating an on-demand basic report about waiting patients and waiting times.

### Future Extension

Additional capabilities may be integrated in future stages according to the requirements of the project.

At the current stage, urgency levels are determined by the triage staff without AI-based decision making.

The full English project proposal is available in `PROJECT_PROPOSAL_EN.md`.