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

The validated business rules are:

- `Patient.age` must be a whole number between 0 and 120.
- `Patient.arrival_time` must be a valid ISO date-time string whose date is today, for example `2026-10-31T06:00:00` when the program runs on 31 October 2026. Dates before or after today are rejected. It is stored in one normalized format so sorting by arrival time stays chronological.
- `Patient.status` must be `waiting`, `in_treatment`, or `completed`.
- `TriageAssessment.pain_level` must be a whole number between 0 and 10.
- `TriageAssessment.urgency_level` must be a whole number between 1 and 5. Values such as `2.5` are rejected.
- `EmergencyQueue.add_patient()` rejects a patient without an assessment and a patient whose `patient_id` is already in the queue.

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

The file contains at least 15 synthetic patient records.

No real personal or medical information is used.

Each line contains one independent JSON object.

Example:

```json
{
  "patient_id": "P001",
  "name": "Daniel Cohen",
  "age": 35,
  "arrival_time": "06:00:00",
  "status": "waiting",
  "assessment": {
    "chief_complaint": "Chest pain",
    "pain_level": 8,
    "urgency_level": 1
  }
}
```

In the data file `arrival_time` holds only the clock time (`HH:MM:SS`). When the file is loaded, `repository.py` combines it with today's date, so the demo data is valid on any day.

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
to_todays_arrival_time()  (adds today's date to the clock time)
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
- An arrival time that is not a valid clock time, reported with the line number.
- Invalid business values through model validation.

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
- `AI_USAGE.md` – project development record.

The assignment allows modules to be split when responsibilities remain clear. Generators and reporting use dedicated modules in this project, and the actual project structure is documented above.

---

## Python Version

The project requires **Python 3.11 or newer**.

This matches:

```toml
requires-python = ">=3.11"
```

in `pyproject.toml`.

The Stage 1 components use the Python standard library. For the current application, install the dependencies described in Stage 2 below before running the demonstration.

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

---

## Stage 2 (שלב 2)

### What Was Added

- Heat alerts help the nurse identify vulnerable waiting patients for reassessment. The system flags and reports patients; it does not change clinical urgency or queue order. Starting treatment clears the flag. The heat report includes the current level, forecast peak and flagged patient IDs.

### Setup and Commands

- Use Python 3.11 or newer and an activated virtual environment. From the repository root, install with `pip install -e ".[dev]"` (requests, python-dotenv and pytest).
- See [.env.example](.env.example) for optional local settings: API URL, hospital coordinates, timeout, retry attempts and delay, forecast hours, sample file and log level. Copy it to `.env` only if needed; never commit `.env`. No API key is required.

```text
python main.py
python main.py --live
python -m pytest
```

- The default runs Stage 1 followed by Stage 2 without network access, using `data/weather_sample.json` and marking it SIMULATED. `--live` selects Open-Meteo and marks the source LIVE; a failed request never falls back to sample data. The failure demonstration, lab results and nurse claims are separately marked `[SIMULATED]`.

### Stage 2 Structure

The Stage 1 modules remain in place. The following tree shows the Stage 2 additions and shared files extended for this stage:

```text
main.py
.env.example
pyproject.toml
er_triage/
    config.py
    api_client.py
    models.py
    strategies.py
    observers.py
    services.py
    reporting.py
    async_processing.py
    threaded_processing.py
data/
    sample_data.jsonl
    weather_sample.json
    lab_results.json
tests/
    conftest.py
    test_*.py
docs/
    T15_LIVE_VERIFICATION.md
```

- `config.py`: environment settings and optional `.env` loading.
- `api_client.py`: live/offline clients, payload validation and connection retry.
- `models.py`: reassessment flags and immutable `WeatherSnapshot` / `HourlyForecast` records alongside the Stage 1 classes.
- `strategies.py`: interchangeable patient selection rules for each heat level.
- `observers.py`: flag events, audit logging and the nurse worklist.
- `services.py`: heat classification, forecast summary and `HeatAlertService` orchestration.
- `reporting.py`: `generate_heat_report()` alongside the unchanged Stage 1 waiting report.
- `async_processing.py`: simulated sequential and concurrent lab result collection.
- `threaded_processing.py`: nurse Threads that claim work until the shared list is empty.
- `main.py` connects dependencies and presents both stages; `tests/` covers individual components, Stage 1 regression and integration.

### API and Error Handling

- [Open-Meteo Forecast API documentation](https://open-meteo.com/en/docs): one GET to `https://api.open-meteo.com/v1/forecast` requests current temperature, apparent temperature and humidity plus hourly apparent temperature. Defaults are Tel Aviv (`32.0853`, `34.7818`), six forecast hours, `timezone=auto` and a five-second timeout. The client calls `raise_for_status()` before reading JSON.
- Validation requires `current` and `hourly` objects, ISO observation/forecast times, current temperature and apparent temperature in −60..60°C, humidity in 0..100, and nonempty, equally sized hourly time/temperature lists with temperatures in −60..60°C. Numeric fields reject booleans. Valid data becomes a snapshot marked `live` or `simulated`; both clients share the parser.
- Four failure categories are handled: communication failure, HTTP error, malformed JSON, and missing/invalid fields. Timeout/connection failures become `WeatherConnectionError` after three attempts by default, with waits of one then two seconds and no final wait. HTTP errors become `WeatherHTTPError`; malformed JSON and invalid fields become `WeatherDataError`. HTTP errors (including authorization failures) and bad data are not retried because repeating the same request does not correct the underlying problem.
- The service catches `WeatherServiceError`, logs a warning, returns `unavailable` and makes no patient changes. It does not substitute sample weather or hide unrelated programming errors. Only `main.py` configures logging; patient logs contain IDs rather than names.

### Rules and Architecture

- The current apparent temperature determines the level: below 32°C is `normal`, 32–below 39°C is `caution`, and 39°C or above is `danger`. These rounded thresholds approximate NWS Heat Index categories; Open-Meteo uses a different apparent-temperature formula, so this is a project assumption rather than an equivalent medical measure.
- Eligible patients are waiting, have urgency above 1 and are not already flagged. Heat-sensitive complaints contain `dizz`, `weak`, `confus`, `breath` or `fever`, case-insensitively. `normal` selects nobody; `caution` requires both age ≥65 and a matching complaint; `danger` requires either. For the sample patients, danger flags exactly `P005` and `P011`, while caution flags only `P011`.
- Strategy maps each level to `NoFlaggingStrategy`, `VulnerableOnlyStrategy` or `AllAtRiskStrategy`, keeping selection rules out of the service. Observer publishes each `PatientFlaggedEvent` to `AuditLogObserver` and `ReassessmentWorklist`, keeping these reactions separate. The worklist is ordered by urgency and arrival time.
- Dependency injection in `main.py` supplies the weather client, publisher, observers and strategy dictionary. Tests can replace the client or HTTP session and retry sleep without using a network or changing the business rules.
- Async lab tasks simulate waiting with `asyncio.sleep`; the demo compares sequential collection with `asyncio.gather`, prints timings and preserves input order in the results. The lab data is fictional, and critical results are identified by its `is_critical` field.
- The shared nurse worklist uses one Lock around checking, selecting and removing a patient, preventing two nurses from claiming the same patient. Without the lock, this order of operations causes the error: nurse A checks that `P011` is waiting, nurse B checks before A removes it, both select `P011`, and the second removal fails with `ValueError: list.remove(x): x not in list` (or the patient would be assessed twice). All Threads start before they are joined; there is no network call inside the lock. Which nurse claims a patient is not deterministic. An empty list produces a message that no actual claims occurred.

### Verification Evidence

- We validated a clean clone at commit `49c2819` with a fresh virtual environment and successful installation. PowerShell results were `131 passed in 2.46s`, an additional run gave `131 passed in 2.14s`, and the final offline run gave `131 passed in 2.15s`. Tests cover validation, error handling and retry, selection rules, observers, reports, Async/Threads, Stage 1 regression, integration, client selection and output order; test weather requests are mocked or read local files.
- A final code review added input validation for the weather client settings, the offline sample file and malformed patient files. The suite now has 142 tests (`142 passed in 1.36s`), and it also passes with all network access blocked.
- With the internet physically disconnected, both pytest and the default `main.py` run succeeded; the demonstration showed SIMULATED source, level `danger`, exactly `P005` and `P011` flagged, and forecast maximum 42.0°C.
- We verified a real LIVE run, recorded in [docs/T15_LIVE_VERIFICATION.md](docs/T15_LIVE_VERIFICATION.md):

```text
Command: python main.py --live
Execution timestamp: 2026-11-02 18:52:19 +02:00
Source: LIVE – Open-Meteo
Status: applied
Observed at: 2026-11-02T18:45
Apparent temperature: 27.3°C
Forecast maximum: 28.5°C
Heat level: normal
Flagged patients: 0
```

- `classify_heat_level` was developed in three separate TDD commits: [Red — failing tests](https://github.com/yairrrr/-ER-Triage-System/commit/1c0672d82a283dffa9aed04ba0c7c6bca356ac8e), [Green — thresholds](https://github.com/yairrrr/-ER-Triage-System/commit/392c72bba5b9212eb5d3692f224c8744f1106408), and [Refactor — named constants](https://github.com/yairrrr/-ER-Triage-System/commit/49cbba051412c66ff854d54ae58dc85949ec94f9). The hashes were verified from Git history.
