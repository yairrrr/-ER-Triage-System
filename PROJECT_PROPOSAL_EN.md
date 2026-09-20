# Project Proposal

## Project Name

ER Triage System – Emergency Room Queue Management and Prioritization System

## System Description

An information system for managing patients in a hospital emergency room. The triage staff determines and updates each patient’s urgency level, while the system manages the order of treatment according to the urgency level and arrival time.

## Business Need

Emergency rooms receive many patients with different levels of urgency. Treating patients only according to their order of arrival may cause a patient with a more serious condition to wait while less urgent patients are treated first.

The purpose of the system is to help the emergency room staff manage the patient queue more efficiently using the urgency level assigned to each patient, while maintaining the order of arrival among patients with the same urgency level.

The system is intended to support queue management according to the medical staff’s assessment and not to replace professional medical decisions.

## Main Users

### Triage Nurse

Registers new patients, enters their initial information, determines their urgency level, and updates it when necessary while they are waiting.

### Doctor

Views waiting patients and their priority order, moves a patient from waiting to treatment, and marks the treatment as completed.

### Emergency Department Manager

Can view the current queue and generate, on demand, a basic report about waiting patients and their waiting times.

## Main Business Process

The process begins when a new patient arrives at the emergency room.

The triage nurse registers the patient in the system and enters the patient’s details and relevant information about their condition.

The triage nurse assigns the patient an urgency level from 1 to 5, where level 1 represents the highest urgency and level 5 represents the lowest urgency.

After the urgency level is determined, the patient is added to the emergency room queue and positioned according to their urgency level and arrival time.

If the patient’s condition changes while waiting, the urgency level can be updated and the system updates the patient’s position in the queue accordingly.

When the medical staff becomes available to receive another patient, the system identifies the next patient who should be treated.

When treatment begins, the patient’s status changes from "waiting" to "in_treatment". When treatment is completed, the status changes to "completed".

In addition, an on-demand function can generate a basic report about the waiting patients and their waiting times.

## Information Flow

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

* Treatment order based on the urgency level assigned by the triage staff
* List of waiting patients
* Updated queue order after a change in urgency level
* Patient status in the process
* An on-demand basic report about waiting patients and waiting times

## Business Value

The system is expected to assist with:

* Giving priority to more urgent patients
* Reducing waiting times for high-priority cases
* Improving the organization and management of the patient queue
* Reducing errors caused by manually managing treatment order
* Providing the medical staff with a clear overview of waiting patients
* Supporting the emergency room staff

## Main Entities and Initial Relationships

### Patient

Represents a person registered in the emergency room.

### TriageAssessment

Represents the information collected during triage and the urgency level assigned to the patient.

### EmergencyQueue

Manages patients waiting for treatment and their priority order.

### MedicalStaff

Represents a system user who participates in the patient registration or treatment process.

Initial relationships:

* Each patient can have a triage assessment.
* The triage assessment contains the urgency level assigned and updated by the triage staff.
* Patients waiting for treatment are placed in the emergency queue.
* Medical staff members register, update, and treat patients.

## Main Use Cases

### Use Case 1 – Registering a New Patient

A patient arrives at the emergency room. The triage nurse enters the patient’s details and initial information, assigns an urgency level, and the system places the patient in the appropriate position in the queue according to the urgency level and arrival time.

### Use Case 2 – Selecting the Next Patient for Treatment

When a medical staff member becomes available to receive another patient, the system identifies the patient with the highest urgency. When multiple patients have the same urgency level, the patient who arrived earlier receives priority.

When treatment begins, the patient’s status changes to "in_treatment", and when treatment is completed, the status changes to "completed".

### Use Case 3 – Updating an Urgency Level

If a waiting patient’s condition changes, the triage nurse can update the patient’s urgency level. The system then updates the patient’s position in the queue accordingly.

### Use Case 4 – Generating a Basic Report

On demand, a function can generate a basic report about the current queue, including waiting patients and their waiting times.

## Future Extension

In a future stage, the system can be expanded with additional capabilities according to the needs of the emergency department and the later stages of the project.

At the current stage, urgency levels are determined by the triage staff without integrating AI into the decision-making process.