# AI Usage

## AI Tool

The AI tool used during this project was ChatGPT by OpenAI.

AI was used to assist with generating the initial synthetic dataset and, during development, for explanations, code review, debugging, and checking the implementation against the assignment requirements.

All generated suggestions were reviewed and tested before being included in the project.

---

## Synthetic Data Generation

AI was used to generate the initial synthetic patient records stored in:

`data/sample_data.jsonl`

The requested dataset contained at least 15 fictional emergency-room patients.

No real personal or medical information was used.

### Final Data Generation Prompt

The AI was asked to generate synthetic emergency-room patient records in JSON format according to the validation rules of the project.

The request was approximately:

> Generate at least 15 fictional emergency-room patient records in JSON format for an ER triage system.
>
> Each record must contain a unique patient ID, patient name, age, arrival time, status, and triage assessment.
>
> The triage assessment must contain a chief complaint, pain level, and urgency level from 1 to 5, where 1 represents the highest medical priority.
>
> Use only fictional data and do not include real personal information.
>
> Return the records in JSONL format, with one valid JSON object per line.

---

## Record Structure

Each generated patient record follows this general structure:

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

### Field Rules

The records must satisfy the validation rules of the business classes in `er_triage/models.py`:

| Field | Rule |
|---|---|
| `patient_id` | Unique across the file |
| `age` | Whole number between 0 and 120 |
| `arrival_time` | Clock time `HH:MM:SS`; the loader adds today's date, and the model accepts only today's date |
| `status` | One of `waiting`, `in_treatment`, `completed` |
| `assessment.pain_level` | Whole number between 0 and 10 |
| `assessment.urgency_level` | Whole number between 1 and 5 (1 = highest priority) |

---

## Data Checks Performed

The generated file was checked in two ways.

### 1. Direct Inspection of the Records

A short Python check read `data/sample_data.jsonl` line by line and verified the records against the rules above. Results:

| Check | Result |
|---|---|
| Every line is valid JSON | 15 of 15 lines parsed |
| Number of records | 15 (the minimum required) |
| Duplicate `patient_id` values | None (`P001`–`P015`) |
| Missing top-level fields | None |
| Missing assessment fields | None |
| `status` values | All 15 records are `waiting` |
| `age` | Whole numbers, range 18–78 |
| `arrival_time` | All valid ISO date-times in one format, range 18:00–18:57 on 2026-09-16 |
| `urgency_level` | Whole numbers only: 1 (×4), 2 (×2), 3 (×4), 4 (×4), 5 (×1) |
| `pain_level` | Whole numbers only, range 2–9 |
| Real personal information | None, all names and complaints are fictional |

The urgency levels were also read against the chief complaints to make sure the data is reasonable for the scenario. For example, chest pain and difficulty breathing are urgency 1, while a sore throat is urgency 5.

### 2. Loading Through the Project Code

The file was loaded with `load_patients()` from `er_triage/repository.py`, which converts every line into `Patient` and `TriageAssessment` objects and runs all model validation. All 15 records were loaded successfully.

To confirm that the loader really rejects bad data, and does not only accept good data, test copies of the file were created outside the repository, each with one deliberate error:

| Deliberate error | Result |
|---|---|
| Truncated JSON line | Rejected: `Invalid JSON on line 3` |
| Record without `age` | Rejected: `Missing fields on line 3: {'age'}` |
| Repeated `P001` record | Rejected: `Duplicate patient ID: P001` |
| `arrival_time` = `"16/09/2026 18:00"` | Rejected: `Invalid arrival time` |
| `urgency_level` = `2.5` | Rejected: `Urgency level must be a whole number between 1 and 5` |
| `urgency_level` = `7` | Rejected: `Urgency level must be a whole number between 1 and 5` |
| `status` = `"discharged"` | Rejected: `Invalid patient status` |
| `age` = `-4` | Rejected: `Age must be a whole number between 0 and 120` |

---

## Problems Found and Fixes

The check with deliberately invalid data showed that some invalid values were accepted by the model before the fix:

| Problem | Before the fix | Fix in `er_triage/models.py` |
|---|---|---|
| Invalid arrival time | `Patient` accepted any value, for example `"16/09/2026 18:00"` or `"yesterday"`. The error appeared only later, when the report tried to compute waiting time. | `arrival_time` is now a property. The setter accepts only a string that `datetime.fromisoformat()` can parse and raises `ValueError` otherwise. The value is stored in one normalized ISO format so sorting by arrival time stays chronological. |
| Non-integer urgency level | `TriageAssessment` accepted `2.5` because only the range 1–5 was checked. | `is_valid_urgency()` now also requires a whole number. `bool`, `float` and `str` are rejected. |
| Same patient added twice to the queue | `EmergencyQueue.add_patient()` added the same patient twice, so the queue length grew to 2 for one patient. | `add_patient()` raises `ValueError` when a patient with the same `patient_id` is already in the queue. The check uses `Patient.__eq__`, which compares `patient_id`. |
| Same gap in other numeric fields | `pain_level` accepted `7.5` and `age` raised `TypeError` instead of `ValueError` for text. | `pain_level` and `age` now also require whole numbers and raise `ValueError` with a clear message. |
| Arrival date not today | After the first fix any valid ISO date was accepted, for example `2035-01-01T10:00:00` or `2020-01-01T10:00:00`. | The `arrival_time` setter also requires the date to be today. The data file stores only the clock time, and `load_patients()` combines it with today's date, so the demo data stays valid on any day. The sample times were moved from 18:00–18:57 to 06:00–06:57 to avoid negative waiting times during the day. |

Each problem was reproduced with the code before the fix, and then checked again after the fix:

- `Patient(..., arrival_time="not-a-date")` raises `ValueError`.
- `Patient(..., arrival_time="2020-01-01T10:00:00")` raises `ValueError` ("Arrival time must be today").
- `TriageAssessment("Headache", 3, 2.5)` raises `ValueError`.
- Calling `add_patient()` twice with the same patient raises `ValueError` and the queue length stays 1.
- Valid values (urgency 1–5, ISO arrival times, a new patient) are still accepted.
- Updating the urgency of an existing assessment to `2.5` raises `ValueError` and keeps the previous value.

`main.py` contains a `Validation` section that demonstrates the invalid arrival time, the arrival date that is not today, the non-integer urgency level and the duplicate patient. Running `python3 main.py` completes successfully, and apart from this new section the output is the same as before the fix.

---

## Additional AI Usage

### ChatGPT

ChatGPT was used during development for explanations, code review, debugging, and checking the implementation against the assignment requirements.

### Claude Code

Claude Code (Anthropic) was used after the lecturer's feedback on Stage 1. It was used to:

- Reproduce the validation gaps listed in the feedback with small Python checks.
- Suggest the validation changes in `er_triage/models.py` and the `Validation` section in `main.py`.
- Run the data checks and the deliberate-error checks described above.

The suggested changes were reviewed, run and checked before they were committed. The responsibility for the code and the decisions remains with the student.
---

## Stage 2

### T1 – Configuration and secrets

- Tool: Claude Code (Anthropic).
- The tool first proposed a plan for the task (file names, variable names, defaults, error messages) and the test cases, without changing code. The plan was approved before any file was created.
- Expected results we defined and checked ourselves:
  - When a variable is not set, the default value is used.
  - A value that cannot be converted, such as `WEATHER_MAX_ATTEMPTS=abc` or `2.5` for a whole-number setting, raises `ValueError` with the variable name in the message.
- What we verified: ran `python -m pytest -v` (6 tests passed); loaded `config.py` with an invalid environment variable and saw the expected error; checked with `git check-ignore` that `.env` is ignored and `.env.example` is not.
- What we decided: the tests check the `read_*` functions and not the module constants, because the constants are read once when the module is imported. The Open-Meteo service needs no API key, so `.env.example` contains only settings and no secrets.

### T2 – Weather model and response validation

- Tool: Claude Code (Anthropic).
- The tool first proposed the data classes, the validation rules for each field and the test cases, without changing code. The plan was approved before the code was written.
- Expected results we defined and checked ourselves:
  - The real Open-Meteo response from 2026-10-29 is converted to a `WeatherSnapshot` with the same values (apparent temperature 24.0, six forecast hours).
  - A missing field, a text value, `True`, an out-of-range value and forecast lists of different length each raise `WeatherDataError` naming the problem.
- What we verified: ran `python -m pytest -v` (18 tests passed); parsed one new live response from the service with `parse_weather_payload` and it was accepted.
- What we decided: the tool suggested also checking that the time fields are valid ISO date-times (stricter than the original plan, which only required a string). We kept this check because the real response passes it.
### T5 – Reassessment flag on the patient

- Tool: Claude Code (Anthropic).
- The tool first proposed the new fields, the method and the test cases, without changing code. The plan was approved before the change was made.
- Decision made by the group: the tool asked whether a patient who is not waiting may be flagged. We decided that `flag_for_reassessment()` raises `ValueError` for such a patient, so the model itself cannot reach an inconsistent state.
- Expected results we defined and checked ourselves:
  - A new patient is not flagged; after `flag_for_reassessment("heat:danger")` it is flagged with that reason.
  - After `start_treatment()` the flag is cleared, and flagging a patient who is `in_treatment` or `completed` raises `ValueError`.
- What we verified: ran `python -m pytest -v` (24 tests passed), including a check that all 15 patients from `data/sample_data.jsonl` still load and are not flagged; ran `python main.py` and the Stage 1 demo still completes.
### T6 – Heat level classification with TDD

- Tool: Claude Code (Anthropic).
- The tool first proposed the test cases (boundary values around 32 and 39) and the three TDD steps, without changing code.
- Expected results we defined ourselves, from the business rule: `31.9` is `normal`, exactly `32` is `caution`, `38.9` is `caution`, exactly `39` is `danger`.
- What we verified: in the Red step the run showed `4 failed, 2 passed` with `AssertionError` (the missing behaviour, not an import error); after Green and after Refactor the full suite passed (30 tests). The test file was not changed after the Red commit.
- What we checked and corrected: the thresholds come from the US National Weather Service heat index categories (90°F = 32.2°C, 103°F = 39.4°C). We rounded them to 32 and 39 and documented in the code that this is an approximation, because Open-Meteo's apparent temperature uses a different formula.
### T11 – Asynchronous lab result collection

- Tool: Claude Code (Anthropic).
- The tool first proposed the business scenario, the functions and the test cases, without changing code.
- Expected results we defined ourselves:
  - With delays of 0.15, 0.05 and 0.10 seconds, the concurrent version returns the results in the input order (`A001`, `A002`, `A003`), although `A002` finishes first.
  - The sequential version takes at least the sum of the delays (about 0.30 s) and the concurrent version takes less than 0.25 s.
- What we verified: ran `python -m pytest -v` (36 tests passed); ran both versions on `data/lab_results.json` and measured 0.303 s (sequential) against 0.152 s (concurrent) with identical results; checked that the async module uses only `asyncio.sleep` and no `time.sleep` or HTTP calls.
- What we decided: the lab values in `data/lab_results.json` are fictional and are not based on medical reference ranges, so whether a result is critical is stored in the data (`is_critical`) and not calculated in the code. Handling a failure of a single task while collecting the others is optional in the assignment and was not implemented.
### T13 – Stage 1 regression tests

- Tool: Claude Code (Anthropic).
- The tool first listed the Stage 1 behaviours to protect and the test cases, without changing code. The list included the cases from the lecturer's feedback (`True` and `"1"` as values, a duplicate patient, an invalid or non-today arrival time).
- Expected results we defined ourselves:
  - With equal urgency, the patient who arrived earlier is first in the queue; a later patient with urgency 1 is taken before an earlier patient with urgency 3.
  - A JSONL line with the clock time `06:30:00` is loaded with today's date, and `25:00:00` on line 2 raises `ValueError` mentioning line 2.
- What we verified: ran `python -m pytest -v` (58 tests passed). The repository tests write their own files in `tmp_path` and do not depend on `data/sample_data.jsonl`.
- What we added beyond the plan: a test that equal urgency is ordered by arrival time, because it is a central Stage 1 rule that was not covered, and a test that today's arrival time is accepted, so the rejection tests cannot pass with code that rejects every date.
