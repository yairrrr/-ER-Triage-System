# ER Triage System

A local Python system for managing and prioritizing patients in a hospital emergency room according to medical urgency and arrival time.

## Project Proposal

### Project Name and System Description

**ER Triage System** is a local Python information system that helps emergency-room staff register, prioritize, track, and process patients according to medical urgency and arrival time.

### Business Need

Emergency departments must manage multiple waiting patients while ensuring that urgent cases receive treatment before less urgent cases. A simple first-come-first-served queue is not sufficient because a patient who arrives later may have a more serious medical condition.

The system provides a structured process for registering patients, recording triage assessments, maintaining a prioritized queue, updating urgency when a patient's condition changes, and selecting the next patient for treatment.

### Main Users

- **Triage Nurse** – registers patients, records triage assessments, assigns urgency levels, and updates urgency when required.
- **Doctor** – receives the next patient selected for treatment and participates in the treatment process.
- **Emergency Department Manager** – uses queue and report information to understand waiting-room activity and support operational decisions.

### Main Business Process

The process begins when a patient arrives at the emergency department and is registered.

A triage nurse records an assessment and assigns an urgency level from 1 to 5:

- `1` – highest urgency
- `5` – lowest urgency

The patient enters the emergency queue.

Patients are prioritized first by urgency level and then by arrival time when urgency levels are equal.

If a patient's condition changes while waiting, the urgency level can be updated and the patient's position in the queue is recalculated.

When a patient is selected for treatment, the status changes:

`waiting → in_treatment`

When treatment is completed:

`in_treatment → completed`

The result is a consistent treatment order based on medical priority while preserving arrival order when priorities are equal.

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

Medical staff create and update this information.

The system converts the input into business objects, maintains the treatment queue, and produces queue information and an on-demand waiting-patient report.

### Expected Business Value

The system helps:

- Prioritize urgent cases consistently.
- Reduce manual queue-management errors.
- Reflect changes in a patient's condition.
- Improve visibility of the current waiting queue.
- Support staff decisions about treatment order.
- Provide basic waiting-time information when requested.

The system supports medical staff decisions and does not independently determine medical urgency.

### Main Entities and Relationships

- `Patient` – represents a patient in the emergency department.
- `TriageAssessment` – represents the patient's triage assessment.
- `EmergencyQueue` – contains and manages patients waiting for treatment.
- `MedicalStaff` – common base class for medical staff.
- `Nurse` – a type of `MedicalStaff`.
- `Doctor` – a type of `MedicalStaff`.

A `Patient` has a `TriageAssessment`, and an `EmergencyQueue` manages a collection of `Patient` objects.

### Main Use Cases

1. Register a patient, create a triage assessment, assign an urgency level, and place the patient in the queue.
2. Select the next patient for treatment according to urgency level and arrival time.
3. Update the urgency level of a waiting patient and reposition the patient accordingly.
4. Move a patient through the statuses `waiting`, `in_treatment`, and `completed`.
5. Generate an on-demand report about waiting patients and waiting times.

### Future Extension

A future stage can connect the system to an external service, add automated tests, and support concurrent operations while keeping the current business model as the foundation.

---

## Object-Oriented Design

### Business Classes and Responsibilities

The project contains multiple business classes with clear responsibilities:

- `Patient` stores patient information and manages patient status and comparison behavior.
- `TriageAssessment` stores triage information and validates urgency-related data.
- `EmergencyQueue` manages the collection and ordering of patients.
- `MedicalStaff` defines shared behavior for medical staff.
- `Nurse` and `Doctor` specialize `MedicalStaff` behavior.

The central model classes use constructors, business operations, alternative constructors where appropriate, `__str__` for friendly display, and `__repr__` for useful development representations.

### Composition

The system uses composition between `Patient` and `TriageAssessment`.

A `Patient` has a `TriageAssessment` object containing information such as chief complaint, pain level, and urgency level.

`EmergencyQueue` also contains a collection of `Patient` objects and provides operations on that collection, including adding patients, removing patients, updating urgency, and selecting the next patient.

### Inheritance and Polymorphism

`MedicalStaff` is the common base class for medical staff.

The system contains two subclasses:

- `Nurse`
- `Doctor`

Both override the `get_role()` method.

Objects of both types can be stored in the same collection and handled through their shared interface:

```python
staff_members = [
    Nurse("S001", "Dana"),
    Doctor("S002", "David")
]

for staff_member in staff_members:
    print(staff_member.get_role())
```

No `if`/`elif` type checking is required. Each object responds using its own implementation of `get_role()`, demonstrating polymorphism.

### Abstract Base Class

`MedicalStaff` is implemented as an abstract base class.

It defines common behavior for medical staff while requiring subclasses to implement role-specific behavior.

### Encapsulation, Properties, and Validation

Business values are validated so objects cannot remain in an invalid business state.

Invalid values raise `ValueError` with an explanatory message.

The project uses properties and validation for controlled access to business fields.

Additional OOP features used by the project include:

- `@classmethod` for alternative construction from dictionaries.
- `@staticmethod` for urgency validation.
- Properties for controlled or calculated values.
- `__len__`
- `__eq__`
- `__lt__`
- `__str__`
- `__repr__`

---

## Data Structures and Collection Processing

### Data Structure Choices

| Need | Structure | Why It Is Suitable |
|---|---|---|
| Ordered collection that can change | `list` | Preserves order and supports modification |
| Short fixed record or multi-field key | `tuple` | Fixed structure and useful for comparisons |
| Unique values and membership checks | `set` | Prevents duplicates and supports efficient membership operations |
| Patient lookup by ID | `dict` | Provides direct key-based lookup |
| Grouping patients by urgency | `dict` | Maps each urgency level to a collection of patients |
| FIFO processing by arrival order | `deque` | Efficient `append()` and `popleft()` operations |
| Processing by medical priority | `heapq` | Efficient retrieval of the next highest-priority item |

### List, Tuple, and Starred Unpacking

A `list` is used for ordered collections that may change.

A `tuple` is used for fixed records and multi-field sorting or priority keys.

The processing code also demonstrates starred unpacking (`*`) to collect remaining values where appropriate.

### Set Operations

Sets are used for unique values and membership operations.

The project demonstrates multiple set operations, including:

- Membership using `in`.
- Intersection between sets.

The program does not rely on the printed order of a set.

### Dictionary Operations

The project uses dictionaries for different purposes:

- A lookup dictionary maps `patient_id` to a `Patient`.
- A grouping dictionary organizes patients by urgency level.

The code demonstrates:

- Iterating over `.items()` with unpacking.
- Using `.get()` when a missing key is an expected situation.
- Explicit handling of duplicate patient IDs.

Duplicate patient IDs are treated as invalid and cause `ValueError`.

### FIFO Queue with `deque`

A `deque` represents a process where arrival order matters.

Patients are added using `append()` and removed using `popleft()`.

The implementation handles an empty queue without crashing.

Arrival order matters because this queue represents a first-in-first-out process. When priority is not the deciding factor, the patient who arrived first should be processed first.

### Priority Queue with `heapq`

A separate priority queue is implemented using `heapq` for a process where medical urgency takes precedence over arrival order.

A smaller urgency number represents higher priority:

- `1` is the highest priority.
- `5` is the lowest priority.

Patients are inserted using `heappush()` and the next patient is retrieved using `heappop()`.

When patients have the same urgency level, additional values such as arrival time provide deterministic tie handling.

The internal heap list is not treated as a fully sorted list.

### Comprehensions

The processing module includes all three required comprehension types:

- List comprehension for filtering or transformation.
- Set comprehension for producing unique values.
- Dict comprehension for creating an index or mapping.

The comprehensions are kept short and readable.

### Sorting and Functions as Values

The project uses `sorted()` with the `key` parameter.

It demonstrates:

- A regular named function as a sorting key.
- A short `lambda` as a sorting key.
- Multi-field sorting using a tuple.

For example:

```text
(urgency_level, arrival_time)
```

Urgency is compared first. Arrival time is used when urgency levels are equal.

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

## Data Source and Incremental JSONL Processing

The project uses synthetic patient data stored in:

`data/sample_data.jsonl`

The file contains at least 15 synthetic patient records generated with AI assistance.

No real personal or medical information is used.

Each line contains one independent JSON object.

Example:

```json
{
  "patient_id": "P001",
  "name": "Daniel Cohen",
  "age": 35,
  "arrival_time": "2026-09-16T18:00:00",
  "status": "waiting",
  "assessment": {
    "chief_complaint": "Chest pain",
    "pain_level": 8,
    "urgency_level": 1
  }
}
```

### Loading Process

`repository.py` opens the file using UTF-8 encoding and processes it one line at a time.

The implementation does not use `read()` or `readlines()` to load the complete file.

Each record follows this process:

```text
JSON line
   ↓
json.loads()
   ↓
dict
   ↓
Patient.patient_from_dict()
   ↓
Patient object
```

When an assessment dictionary is present, `TriageAssessment.from_dict()` converts it into a `TriageAssessment` object.

The repository checks for:

- Invalid JSON.
- Missing required fields.
- Duplicate patient IDs.
- Invalid business values through model validation.

The synthetic dataset was generated with AI assistance. The AI tool, generation prompt, record structure, validation process, corrections, and verification are documented in `AI_USAGE.md`.

---

## Iterable and Iterator

The project implements two separate classes:

- `WaitingPatients` – the iterable collection.
- `WaitingPatientIterator` – the iterator that stores traversal state.

`WaitingPatients.__iter__()` creates a new `WaitingPatientIterator` every time `iter()` is called.

The iterator implements:

- `__iter__()`
- `__next__()`

It returns patients according to its waiting-patient traversal rule.

When no additional matching patients exist, it raises `StopIteration`.

### Independent Iterators

Two iterators can traverse the same collection independently:

```python
iterator_one = iter(waiting_patients)
iterator_two = iter(waiting_patients)
```

Each iterator stores its own position.

Advancing `iterator_one` does not change the position of `iterator_two`.

---

## Generator

The project contains a generator that uses `yield` to gradually return patients that satisfy a business condition, such as patients whose status is `waiting`.

Creating the generator does not immediately process the complete collection.

A call to `next()` retrieves the next matching patient.

A subsequent `for` loop continues from the exact position where the generator stopped:

```python
waiting_generator = waiting_patients_generator(patients)

first_patient = next(waiting_generator)

for patient in waiting_generator:
    print(patient)
```

After the generator reaches the end, it is exhausted and cannot restart.

To traverse the data again from the beginning, a new generator object must be created.

---

## Lazy Generator Pipeline

The project implements a lazy processing pipeline with at least three stages:

```text
all patients
    ↓
waiting patients
    ↓
requested urgency level
    ↓
patient_id
```

The stages are:

1. Filter patients whose status is `waiting`.
2. Filter those patients according to the requested urgency level.
3. Return the `patient_id` of each matching patient.

No intermediate lists are created between the stages.

### What Starts the Pipeline?

Creating the pipeline does not process all patient records.

Processing begins only when a value is requested, for example:

```python
next(urgent_waiting)
```

### Partial Consumption

The demonstration consumes only the first two results and then stops.

After the second required result is found, later records that are not required do not need to be processed.

### List Comprehension vs. Lazy Generator Processing

A list comprehension creates the complete result immediately.

A generator produces values only when they are requested.

This avoids unnecessary processing and intermediate collections when only part of the result is needed.

### Starting Again

A generator maintains its current state.

To traverse the pipeline again from the beginning, a new generator must be created.

---

## Context Manager

The project implements a custom context manager named `TriageSession`.

It represents a work session and measures its duration.

When entering the `with` block, `__enter__()` records the required start information.

When leaving the block, `__exit__()` records the end information and calculates the session duration.

Example:

```python
with TriageSession("Yair") as session:
    report = generate_waiting_report(patients)
```

### Behavior During an Exception

The project also demonstrates an exception occurring inside a `with` block.

Even when an exception occurs, `__exit__()` still executes.

This proves that the exit operation is performed during an error as required.

The context manager does not hide the exception by returning `True`. The exception remains available to surrounding exception-handling code.

---

## Waiting-Patient Report

The project provides an on-demand waiting-patient report:

```python
generate_waiting_report(patients)
```

The report summarizes the current waiting-room situation and includes waiting-patient information and waiting-time measures.

The report is generated only when requested.

---

## Project Structure

```text
ER-Triage-System/
│
├── main.py
├── README.md
├── AI_USAGE.md
├── PROJECT_PROPOSAL.md
├── PROJECT_PROPOSAL_EN.md
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

### File Responsibilities

- `er_triage/models.py` – business classes, composition, inheritance, polymorphism, validation, and business operations.
- `er_triage/repository.py` – incremental JSONL loading, validation, and conversion from dictionaries to objects.
- `er_triage/processing.py` – data structures, comprehensions, collection processing, and sorting.
- `er_triage/iterators.py` – custom iterable and iterator.
- `er_triage/generators.py` – generators and the lazy processing pipeline.
- `er_triage/context_managers.py` – custom context manager.
- `er_triage/reporting.py` – on-demand waiting-patient reporting.
- `er_triage/__init__.py` – package definition.
- `data/sample_data.jsonl` – synthetic JSONL dataset.
- `main.py` – complete demonstration scenario. Business classes are not defined in this file.
- `README.md` – project description, design decisions, structure, and run instructions.
- `AI_USAGE.md` – documentation of significant AI usage and synthetic-data generation.

The assignment allows modules to be split when responsibilities remain clear. Generators and reporting use dedicated modules in this project, and the actual project structure is documented above.

---

## Python Version

The project requires **Python 3.11 or newer**.

This matches:

```toml
requires-python = ">=3.11"
```

in `pyproject.toml`.

The current project stage uses the Python standard library and does not require additional external packages.

---

## Running the Project

### 1. Clone the Repository

Clone the GitHub repository and enter the project directory.

### 2. Create a Virtual Environment

```bash
python3 -m venv .venv
```

### 3. Activate the Virtual Environment

On macOS or Linux:

```bash
source .venv/bin/activate
```

On Windows:

```text
.venv\Scripts\activate
```

### 4. Run the Demonstration

From the project root:

```bash
python3 main.py
```

The demonstration loads `data/sample_data.jsonl`, converts dictionaries into business objects, and demonstrates:

- Object-oriented design.
- Composition.
- Inheritance and polymorphism.
- Validation.
- Emergency-queue operations.
- Urgency updates.
- Patient status transitions.
- Lists, tuples, sets, and dictionaries.
- FIFO processing with `deque`.
- Priority processing with `heapq`.
- Comprehensions.
- Sorting and lambda expressions.
- Two independent custom iterators.
- Generator behavior.
- Lazy pipeline and partial consumption.
- Context manager during normal execution.
- Context manager during an exception.
- Waiting-patient reporting.