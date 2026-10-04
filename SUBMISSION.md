# ER Triage System - Stage 1 Submission

## GitHub Repository

Public GitHub repository:

https://github.com/yairrrr/-ER-Triage-System

---

# Part A - Project Selection and Initial Specification

## Project Name

**ER Triage System**

## System Description

ER Triage System is a local Python information system for managing and prioritizing patients in a hospital emergency department according to medical urgency and arrival time.

## Business Need

An emergency department cannot always treat patients only according to arrival order.

A patient who arrives later may have a more urgent medical condition and therefore require treatment before patients who arrived earlier.

The system provides a structured way to register patients, record triage assessments, prioritize the waiting queue, update urgency levels when a patient's condition changes, and select the next patient for treatment.

## Main Users

### Triage Nurse

The triage nurse:

- Registers patients.
- Records triage assessments.
- Assigns urgency levels.
- Updates urgency when a patient's condition changes.

### Doctor

The doctor receives patients selected for treatment and participates in the treatment process.

### Emergency Department Manager

The manager can use queue information and reports to understand the current waiting-room situation and support operational decisions.

## Main Business Process

The process begins when a patient arrives at the emergency department.

The patient is registered and receives a triage assessment.

The triage nurse assigns an urgency level from 1 to 5:

- `1` = highest medical priority.
- `5` = lowest medical priority.

The patient is then placed in the emergency queue.

Patients are ordered first by urgency level and then by arrival time when urgency levels are equal.

If the patient's condition changes, the urgency level can be updated and the patient is repositioned accordingly.

When treatment begins:

`waiting → in_treatment`

When treatment is completed:

`in_treatment → completed`

The result is a treatment order that reflects medical priority while preserving arrival order when patients have equal priority.

## Information Flow

The system receives:

- Patient ID.
- Patient name.
- Age.
- Arrival time.
- Patient status.
- Chief complaint.
- Pain level.
- Urgency level.

Medical staff create and update the information.

The information is converted into business objects and used to maintain the emergency queue and generate waiting-patient information.

## Expected Business Value

The system is designed to:

- Prioritize urgent cases consistently.
- Reduce manual queue-management errors.
- Reflect changes in patient urgency.
- Improve visibility of the waiting queue.
- Support treatment-order decisions.
- Provide waiting-time information when requested.

The system supports medical staff decisions and does not independently determine medical urgency.

## Main Entities and Relationships

The main entities are:

- `Patient`
- `TriageAssessment`
- `EmergencyQueue`
- `MedicalStaff`
- `Nurse`
- `Doctor`

A `Patient` has a `TriageAssessment`.

An `EmergencyQueue` manages a collection of `Patient` objects.

`Nurse` and `Doctor` are types of `MedicalStaff`.

## Main Use Cases

1. Register a patient, create a triage assessment, assign an urgency level, and add the patient to the queue.
2. Select the next patient according to urgency level and arrival time.
3. Update the urgency level of a waiting patient and reposition the patient.
4. Move a patient through the statuses `waiting`, `in_treatment`, and `completed`.
5. Generate an on-demand report about waiting patients.

## Future Extension

Future stages can add an external service, automated tests, and concurrency while keeping the current business model as the foundation.

---

# Part B - Object-Oriented Model

The main OOP implementation is located in:

`er_triage/models.py`

## 1. Business Classes and Responsibilities

The project contains more than four business classes with real responsibilities.

### Patient

`Patient` represents a patient in the emergency department.

It stores patient information, status, arrival time, and the patient's triage assessment.

### TriageAssessment

`TriageAssessment` represents the medical triage information associated with a patient.

It contains information such as:

- Chief complaint.
- Pain level.
- Urgency level.

### EmergencyQueue

`EmergencyQueue` manages patients and their treatment priority.

It provides operations such as:

- Adding a patient.
- Removing a patient.
- Selecting the next patient.
- Updating patient urgency.
- Managing patient status.

### MedicalStaff

`MedicalStaff` is the common base class for medical staff.

### Nurse

`Nurse` represents a nurse and inherits from `MedicalStaff`.

### Doctor

`Doctor` represents a doctor and inherits from `MedicalStaff`.

The central classes use meaningful attributes, constructors, business operations, `__str__`, and `__repr__`.

Alternative construction from dictionaries is implemented using `@classmethod` where appropriate.

## 2. Composition

The project contains a composition relationship between:

`Patient` and `TriageAssessment`

A patient has a triage assessment.

`EmergencyQueue` also contains a collection of patients and provides multiple operations on that collection.

This represents a real "has-a" relationship.

## 3. Inheritance and Polymorphism

The base class is:

`MedicalStaff`

The subclasses are:

- `Nurse`
- `Doctor`

Both subclasses override:

```python
get_role()
```

The project demonstrates polymorphism by storing different medical-staff objects in the same collection:

```python
staff_members = [
    Nurse("S001", "Dana"),
    Doctor("S002", "David")
]

for staff_member in staff_members:
    print(staff_member.get_role())
```

The code does not use `if`/`elif` to determine the object's concrete type.

Each object responds using its own implementation of `get_role()`.

## 3.1 Abstract Base Class

The project also uses an abstract base class.

`MedicalStaff` defines shared behavior and requires subclasses to implement role-specific behavior.

This is an additional design choice and does not replace the inheritance and polymorphism requirements.

## 4. Encapsulation, Properties, and Validation

The system validates business values so that objects cannot remain in an invalid state.

Invalid values raise:

```python
ValueError
```

with an explanatory message.

Validation is used for multiple business fields, including patient and triage information.

Properties are used to control access to validated fields.

## 5. Additional Python OOP Features

The project uses several additional features from the course material.

### `@classmethod`

Used for alternative object construction from dictionaries, including conversion of loaded JSON data into business objects.

### `@staticmethod`

Used for a helper operation related to urgency validation.

### Properties

Used for controlled access and validation of business fields.

### `__len__`

Used to return the number of patients in the emergency queue.

### `__eq__`

Used for equality comparison between patients.

### `__lt__`

Used to define ordering between patients according to priority information.

### `__str__`

Used for user-friendly object display.

### `__repr__`

Used for useful development-oriented object representation.

---

# Part C - Data Structures and Collection Processing

The collection-processing implementation is located mainly in:

`er_triage/processing.py`

## 1. List and Tuple

### List

A `list` is used for ordered collections that can change.

For example, patient collections are stored in lists when order must be preserved and items may be added or removed.

### Tuple

A `tuple` is used for short fixed records and multi-field comparison keys.

For example, patient priority can conceptually be represented using:

```text
(urgency_level, arrival_time)
```

### Starred Unpacking

The processing code demonstrates the use of `*` to collect remaining values where appropriate.

---

## 2. Set

A `set` is used when values must be unique or when membership checks are required.

The project demonstrates multiple set operations, including:

- Membership using `in`.
- Intersection between sets.

Set elements are hashable.

The program does not rely on the printed order of a set.

---

## 3. Dictionary

The project uses at least two dictionaries with different purposes.

### Patient Lookup Dictionary

Maps:

```text
patient_id → Patient
```

This allows direct patient lookup by ID.

### Grouping Dictionary

Groups patients according to urgency level.

The project also demonstrates:

- Iteration over `.items()` with unpacking.
- `.get()` when a missing key is an expected situation.
- Explicit duplicate-ID handling.

If a duplicate patient ID is detected, the project raises:

```python
ValueError
```

instead of silently replacing the existing patient.

---

## 4. FIFO Queue with deque

The project uses:

```python
collections.deque
```

for a process where arrival order is important.

Patients are added using:

```python
append()
```

and removed using:

```python
popleft()
```

The implementation handles an empty queue without crashing.

Arrival order is important because FIFO processing means the patient who arrived first is processed first when priority is not the deciding factor.

---

## 5. Priority Queue with heapq

The project uses:

```python
heapq
```

for a process where medical urgency takes priority over simple arrival order.

Patients are inserted using:

```python
heappush()
```

and the next patient is retrieved using:

```python
heappop()
```

A smaller urgency number represents higher priority.

Therefore:

```text
urgency 1 > urgency 2 > urgency 3 > urgency 4 > urgency 5
```

in terms of medical priority.

When urgency levels are equal, additional values such as arrival time are used for correct tie handling.

The internal heap list is not treated as a fully sorted list.

---

## 6. Comprehensions

The project implements all three required comprehension types.

### List Comprehension

Used for filtering or transforming patient information.

### Set Comprehension

Used for producing unique values.

### Dict Comprehension

Used for creating an index or mapping.

The comprehensions are kept short and readable.

---

## 7. Sorting and Functions as Values

The project uses:

```python
sorted()
```

with the `key` parameter.

It demonstrates:

- A regular named function as a sorting key.
- A short `lambda` as a sorting key.
- Multi-field sorting using a tuple.

For example:

```text
(urgency_level, arrival_time)
```

Urgency is compared first.

Arrival time is used when urgency levels are equal.

---

## Operations That Modify a Collection vs. Create a New Collection

| Operation | Behavior |
|---|---|
| `EmergencyQueue.add_patient()` | Modifies the existing queue |
| `EmergencyQueue.remove_patient()` | Modifies the existing queue |
| `deque.append()` | Modifies the existing deque |
| `deque.popleft()` | Modifies the existing deque |
| `heapq.heappush()` | Modifies the existing heap |
| `heapq.heappop()` | Modifies the existing heap |
| `sorted()` | Creates a new sorted list |
| List comprehension | Creates a new list |
| Set comprehension | Creates a new set |
| Dict comprehension | Creates a new dictionary |

---

# Part D - Iterators, Generators, Lazy Evaluation, File Processing, and Context Managers

## 1. Custom Iterable and Iterator

The project implements two separate classes:

- `WaitingPatients`
- `WaitingPatientIterator`

`WaitingPatients` is the iterable collection.

`WaitingPatientIterator` stores the traversal state.

The iterable implements:

```python
__iter__()
```

The iterator implements:

```python
__iter__()
__next__()
```

When traversal is complete:

```python
StopIteration
```

is raised.

Every call to:

```python
iter(waiting_patients)
```

creates a new iterator.

The project demonstrates two independent iterators:

```python
iterator_one = iter(waiting_patients)
iterator_two = iter(waiting_patients)
```

Each iterator stores its own position.

Advancing `iterator_one` does not advance `iterator_two`.

---

## 2. Generator with yield

The project contains a generator that gradually returns patients satisfying a business condition.

The generator uses:

```python
yield
```

Creating the generator does not process the entire collection immediately.

The demonstration performs:

```python
waiting_generator = waiting_patients_generator(patients)
first_patient = next(waiting_generator)
```

and then continues from the same position:

```python
for patient in waiting_generator:
    print(patient)
```

The `for` loop continues from the position after the previous `next()` call.

After the generator reaches the end, it is exhausted.

To start again from the beginning, a new generator must be created.

---

## 3. Lazy Processing Pipeline

The project implements a lazy pipeline with three stages:

```text
all patients
    ↓
waiting patients
    ↓
requested urgency level
    ↓
patient_id
```

### Stage 1

Filter patients whose status is:

```text
waiting
```

### Stage 2

Filter according to the requested urgency level.

### Stage 3

Return the patient's:

```text
patient_id
```

No intermediate lists are created between the stages.

Only the first two results are consumed.

### What Causes the Pipeline to Start Working?

Creating the pipeline does not process the entire collection.

Processing begins when a value is requested, for example:

```python
next(urgent_waiting)
```

### Which Items Are Not Processed?

After the second required result is produced, processing stops.

Later patient records that are not required for those two results do not need to be processed.

### List Comprehension vs. Generator Processing

A list comprehension creates the complete result immediately.

A generator produces values only when they are requested.

This reduces unnecessary processing and avoids creating intermediate collections when only part of the result is required.

### Why Is a New Generator Required?

A generator stores its traversal state.

After it has been consumed, it does not automatically return to the beginning.

A new generator must be created for another traversal from the start.

---

## 4. Incremental File Processing

The synthetic data is stored in:

`data/sample_data.jsonl`

The file contains at least 15 synthetic patient records created with AI assistance.

No real personal information is used.

Each line contains one JSON object.

The file is opened using:

```python
with open(file_path, encoding="utf-8")
```

and processed one line at a time.

The project does not use:

```python
read()
```

or:

```python
readlines()
```

to load the complete file.

Each line is converted using:

```python
json.loads()
```

which creates a Python dictionary.

The dictionary is then converted into a business object using alternative constructors such as:

```python
Patient.patient_from_dict()
```

and:

```python
TriageAssessment.from_dict()
```

The loading process checks:

- Patient IDs.
- Duplicate IDs.
- Missing required fields.
- Invalid JSON.
- Invalid business values.

---

## 5. Custom Context Manager

The project implements:

```python
TriageSession
```

as a custom context manager.

It implements:

```python
__enter__()
__exit__()
```

The context manager measures a work session and stores the information required to calculate its duration.

Normal usage:

```python
with TriageSession("Yair") as session:
    report = generate_waiting_report(patients)
```

### Exception Handling

The project also demonstrates an exception occurring inside the `with` block.

Even when the exception occurs:

```python
__exit__()
```

still executes.

This proves that the exit operation is performed even when an error occurs.

The context manager does not hide the exception by returning `True`.

The exception can therefore be handled by surrounding exception-handling code.

---

# Part E - Project Structure and Execution

## Project Structure

The actual project structure is:

```text
ER-Triage-System/
│
├── main.py
├── README.md
├── AI_USAGE.md
├── PROJECT_PROPOSAL.md
├── PROJECT_PROPOSAL_EN.md
├── SUBMISSION.md
├── pyproject.toml
├── .gitignore
│
├── data/
│   └── sample_data.jsonl
│
└── er_triage/
    ├── __init__.py
    ├── models.py
    ├── repository.py
    ├── processing.py
    ├── iterators.py
    ├── generators.py
    ├── context_managers.py
    └── reporting.py
```

The assignment allows modules to be split when responsibilities remain clear.

In this project, generators and reporting use dedicated modules, and the actual structure is documented in the project documentation.

## File Responsibilities

### `er_triage/models.py`

Contains:

- Business classes.
- Composition.
- Inheritance.
- Polymorphism.
- Validation.
- Business operations.

### `er_triage/repository.py`

Contains:

- JSONL loading.
- Dictionary conversion.
- Data validation.
- Object creation.

### `er_triage/processing.py`

Contains:

- Data-structure processing.
- Comprehensions.
- Sorting.
- Collection operations.

### `er_triage/iterators.py`

Contains the custom iterable and iterator.

### `er_triage/generators.py`

Contains generator functions and the lazy processing pipeline.

### `er_triage/context_managers.py`

Contains the custom context manager.

### `er_triage/reporting.py`

Contains on-demand reporting logic.

### `er_triage/__init__.py`

Defines the Python package.

### `data/sample_data.jsonl`

Contains the synthetic patient dataset.

### `main.py`

Contains the complete demonstration scenario.

Business classes are not defined in `main.py`.

### `README.md`

Contains the project description, design explanations, data-structure decisions, lazy-processing explanation, project structure, Python version, and run instructions.

### `AI_USAGE.md`

Documents AI usage, synthetic-data generation, validation, corrections, and verification.

### `.gitignore`

Prevents environment files, IDE files, cache files, secrets, and other unnecessary local files from being committed.

### `pyproject.toml`

Contains Python project configuration.

---

## Main Demonstration

Running:

```bash
python3 main.py
```

loads:

```text
data/sample_data.jsonl
```

converts dictionaries into business objects and demonstrates:

- OOP.
- Composition.
- Inheritance.
- Polymorphism.
- Validation.
- Data structures.
- Collection processing.
- Comprehensions.
- Sorting.
- Two independent iterators.
- Generator behavior.
- Lazy pipeline.
- Partial generator consumption.
- Context manager during normal execution.
- Context manager during an exception.
- Waiting-patient reporting.

---

## Python Version

The project requires:

**