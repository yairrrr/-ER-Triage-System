# ER Triage System

A decision-support system for managing and prioritizing patients in a hospital emergency room.

## Project Proposal

The system is designed to help emergency room staff manage the patient queue according to urgency level and arrival time. A new patient is registered in the system together with initial information about their condition, receives an urgency level from 1 to 5, and is placed in the queue according to the assigned priority.

The purpose of the system is to give priority to urgent cases, reduce waiting times for high-priority patients, and provide the medical staff with a clear overview of the patients currently waiting.

The system is intended to serve as a decision-support tool and not as a replacement for professional medical decisions made by the medical staff.

### Main Users

- Triage Nurse
- Doctor
- Emergency Department Manager

### Main Entities

- `Patient` – Patient
- `TriageAssessment` – Triage assessment
- `EmergencyQueue` – Emergency room queue
- `MedicalStaff` – Medical staff member

### Main Use Cases

1. Registering a new patient, determining their urgency level, and placing them in the appropriate position in the queue.
2. Selecting the next patient for treatment according to urgency level and arrival time.

### Future Extension

In a future stage, a local AI model will be integrated using Ollama with `gemma4:12b`. The model will receive relevant patient information and assist in recommending an appropriate urgency level.

The full English project proposal is available in `PROJECT_PROPOSAL_EN.md`.