Project Proposal

Project Name

ER Triage System – Intelligent Emergency Room Queue Management and Prioritization System

System Description

An information system for managing patients in a hospital emergency room. The system assists in classifying the urgency level of each patient and managing the order of treatment according to the severity of the patient’s condition and their arrival time.

Business Need

Emergency rooms receive many patients with different levels of urgency. Treating patients only according to their order of arrival may cause a patient with a more serious condition to wait while less urgent patients are treated first.

The purpose of the system is to help the emergency room staff manage the patient queue more efficiently by assigning a priority level to each patient while maintaining the order of arrival among patients with a similar urgency level.

The system is intended to serve as a decision-support tool and not as a replacement for professional medical decisions made by the medical staff.

Main Users

Triage Nurse
Registers new patients in the system and enters their initial information.

Doctor
Views the waiting patients and their priority order and treats the next patient according to the queue.

Emergency Department Manager
Can view the current queue, patient load, and different urgency levels for monitoring and decision-making purposes.

Main Business Process

The process begins when a new patient arrives at the emergency room.

The triage nurse registers the patient in the system and enters the patient’s details and relevant information about their condition.

The system assigns the patient an urgency level from 1 to 5, where level 1 represents the highest urgency and level 5 represents the lowest urgency.

After the urgency level is determined, the patient is added to the emergency room queue and positioned according to their urgency level and arrival time.

When the medical staff becomes available to receive another patient, the system helps identify the next patient who should be treated.

The result is a queue that gives priority to urgent cases while maintaining a fair order among patients with similar urgency levels.

Information Flow

Information enters the system when a new patient is registered and includes:

* Patient ID
* Age
* Arrival time
* Main complaint
* Initial information describing the patient’s condition
* Urgency level
* Patient status in the process

The information is mainly created and updated by the emergency room staff.

Based on this information, the system provides:

* Patient urgency level
* Recommended treatment order
* List of waiting patients
* Patient status in the emergency room process
* Summary information about the current queue

Business Value

The system is expected to assist with:

* Giving priority to more urgent patients
* Reducing waiting times for high-priority cases
* Improving the organization and management of the patient queue
* Reducing errors caused by manually managing treatment order
* Providing the medical staff with a clear overview of waiting patients
* Supporting the emergency room staff’s decision-making process

Main Entities and Initial Relationships

Patient
Represents a person registered in the emergency room.

TriageAssessment
Represents the information collected to determine the patient’s urgency level.

EmergencyQueue
Manages patients waiting for treatment and their priority order.

MedicalStaff
Represents a system user who participates in the patient registration or treatment process.

Initial relationships:

* Each patient can have a triage assessment.
* The triage assessment determines the patient’s urgency level.
* Patients waiting for treatment are placed in the emergency queue.
* Medical staff members register, update, and treat patients.

Main Use Cases

Use Case 1 – Registering a New Patient

A patient arrives at the emergency room. The triage nurse enters the patient’s details and initial information into the system. The system determines an urgency level for the patient and places the patient in the appropriate position in the queue.

Use Case 2 – Selecting the Next Patient for Treatment

When a medical staff member becomes available to receive another patient, the system evaluates the waiting patients and identifies the patient with the highest urgency level. When multiple patients have the same urgency level, their arrival time can be used to determine their order.

Future Extension

In a future stage, a local AI model can be integrated using Ollama with gemma4:12b. The model will receive the patient’s relevant information and assist in recommending an appropriate urgency level.

The system can also be expanded with external services, testing, and concurrent processing mechanisms according to the later stages of the project.