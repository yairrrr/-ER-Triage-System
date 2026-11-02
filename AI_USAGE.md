# AI Usage

## AI Tool

The AI tools documented in this project are ChatGPT and OpenAI Codex by OpenAI, and Claude Code by Anthropic. Their roles are described in the entries below.

AI was used to assist with generating the initial synthetic dataset and, during development, for explanations, code review, debugging, and checking the implementation against the assignment requirements.

The task entries below record the review and validation performed; where historical details cannot be established, that limitation is stated explicitly.

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

`PART2_WORK_PLAN.md` was prepared with AI assistance; its initial commit `633e4b5` records Claude Opus 5.5 as a co-author. The team owns the requirements, planning decisions, review and final approval; the tool supported preparation of the plan.

### T0 – Repository setup and lecturer feedback on arrival time

- Tool: Claude Code (Anthropic). The task was done step by step with the tool's guidance; the student made the setup changes (dependencies in `pyproject.toml`, the `tests` package with shared fixtures in `conftest.py`, and `*.egg-info/` in `.gitignore`).
- The tool found that the virtual environment had been copied from another project and pointed to a path that did not exist; it was deleted and recreated before installation.
- Lecturer feedback: valid ISO dates in any year were still accepted as arrival times. The tool presented options and their consequences; the group decided that only today's date is valid, that the data file stores only the clock time and the loader adds today's date, and that the sample times move from 18:00–18:57 to 06:00–06:57 to avoid negative waiting times during the day.
- The student changed `models.py`, `repository.py`, the sample data and `conftest.py`; at the student's request the tool added the "Arrival date check" demonstration to `main.py` and updated the related documentation.
- What we verified: `pip install -e ".[dev]"` succeeded, `python -m pytest` ran without import errors (no tests existed yet), `python main.py` completed with arrival times of the current day, and an arrival date of 2020-01-01 was rejected with "Arrival time must be today".

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

### T3 – GET request, error handling and Retry

- Tool: Claude Code (Anthropic).
- The tool first proposed the client structure, the retry rules and the test cases, without changing code. The test code was run against our implementation outside the repository before it was added.
- Expected results we defined ourselves:
  - Three `ConnectionError`s raise `WeatherConnectionError` after exactly 3 calls, with waits of 1 and then 2 seconds.
  - HTTP 401 raises `WeatherHTTPError` after a single call, without retry.
- What we verified: ran `python -m pytest -v` (67 tests passed, no network and no real waiting); sent one real request on 2026-10-31 and received an apparent temperature of 21.9°C (level `normal`) with six forecast hours; sent one request with latitude 999 and the real service returned HTTP 400, which became `WeatherHTTPError` with a single attempt.
- What we decided: the session and the sleep function are passed in through the constructor, so the tests replace the network and the waiting and not the function under test. Only `Timeout` and `ConnectionError` are retried; HTTP errors, invalid JSON and invalid fields are not, because a new attempt would return the same answer. Special handling of 429 and 503 is optional and was not implemented.

### T4 – Offline weather client and demo data

- Tool: Claude Code (Anthropic).
- The tool first proposed the sample file, the client and the test cases, without changing code. The test code was run against our implementation outside the repository before it was added.
- Expected results we defined ourselves:
  - `data/weather_sample.json` is loaded with `source="simulated"`, an apparent temperature of 40.5 (level `danger`) and a forecast maximum of 42.0.
  - A sample file with `"hot"` as the apparent temperature is rejected with `WeatherDataError`, exactly like a live response with the same value.
- What we verified: ran `python -m pytest -v` (72 tests passed); loaded the demo file and a missing file by hand and saw the expected results and log messages.
- What we decided: the sample data is fictional and describes a summer day, so that the demo shows patients being flagged; the real service returned about 22°C at the time of development. The offline client uses the same validation function and the same error types as the live client, so a broken demo file is handled like a failed request, and its data is always marked as simulated.

### T7 – Strategy pattern: flagging rules

- Tool: Claude Code (Anthropic).
- The tool first proposed the class structure and the test cases, without changing code. The test code was run against our implementation outside the repository before it was added.
- Expected results we defined ourselves, before any code existed, and that the tests check on `data/sample_data.jsonl`:
  - At the `danger` level exactly `P005` and `P011` are selected.
  - At the `caution` level only `P011` is selected (`P005` is 52 years old).
- What we verified: ran `python -m pytest -v` (88 tests passed); checked that `strategies.py` contains no type checks; checked the age boundary (64 is not at risk, 65 is).
- What we decided: the list of heat-sensitive words and the age 65 are decisions of the group and are kept as constants in one place. The conditions shared by all strategies (waiting, urgency above 1, not already flagged) are written once in the base class. A third strategy that selects nobody is used for the `normal` level, so the service does not need a condition on the heat level.

### T8 – Observer pattern: flag event, audit log and nurse worklist

- Tool: Claude Code (Anthropic).
- The tool first proposed the event, the publisher, the two observers and the test cases, without changing code. The test code was run against our implementation outside the repository before it was added.
- Expected results we defined ourselves:
  - One published event creates exactly one audit entry, `Patient O001 flagged for reassessment (heat level: danger)`, and adds the patient to the nurse worklist.
  - The worklist is ordered by urgency and then by arrival time, and a patient who started treatment leaves it without any change to the worklist itself.
- What we verified: ran `python -m pytest -v` (97 tests passed); checked that the log contains the patient ID and not the name; checked that the publisher works with any object that has `notify()`, without type checks.
- What we corrected: the module file was first created in the `tests` folder by mistake and was moved to `er_triage/` with `git mv`.
- What we decided: the worklist reads the flag from the patient, so starting treatment removes the patient from the list automatically. At this stage, `claim_next()` is not thread-safe yet; the lock is added in T12.

### T12 – Threads and Lock on the nurse worklist

- Tool: Claude Code (Anthropic).
- The tool first explained the race condition and proposed the lock placement and the test cases, without changing code. The test code was run five times against our implementation outside the repository before it was added.
- Expected results we defined ourselves:
  - Five flagged patients and four nurses: exactly five claims, no patient claimed twice, and an empty worklist at the end.
  - One patient and six nurses: exactly one claim, and no nurse fails.
- What we verified: ran the full test suite three times in a row (103 tests passed each time). The tests check the number of claims and the final state, not which nurse took which patient. In an experiment outside the repository the lock was replaced by an object that does not lock and a 1 ms pause was added between the check and the removal: three of four nurse threads failed with `ValueError: list.remove(x): x not in list`, because two nurses had selected the same patient. With the real lock the same experiment finished without errors.
- What we decided: one lock protects the whole check-select-remove sequence and every other access to the shared list. Sorting moved to a private method that does not lock, because `threading.Lock` is not re-entrant and `claim_next()` would otherwise wait for itself. Each nurse has her own result list, so only the worklist is shared.

### T9 – Heat alert service

- Tool: Claude Code (Anthropic).
- The tool first proposed how the service connects the weather client, the heat classification, the strategies and the publisher, and listed the test cases, without changing code. The test code was run against our implementation outside the repository before it was added.
- Expected results we defined ourselves, before any code existed:
  - On `data/sample_data.jsonl` an apparent temperature of 40 flags exactly `P005` and `P011`, and 35 flags only `P011`.
  - When the weather service fails (connection, HTTP or invalid data), nobody is flagged, the audit log and the worklist stay empty, and the result is `unavailable`.
- What we verified: ran `python -m pytest -v` (116 tests passed after bringing in T12). Only the weather client is replaced by a mock; the service, strategies and observers in the tests are the real ones.
- What we decided: the service catches only `WeatherServiceError`, so a real bug (for example `RuntimeError`) is not reported as an unavailable service. The strategy is taken from a dictionary by heat level, so the service has no condition on the level. A patient is flagged before the event is published, because the worklist shows only flagged patients. The service checks at creation that a strategy exists for every heat level.

### T10 – Heat report

- Tool: Claude Code (Anthropic).
- The tool first proposed the report fields and the forecast summary, and listed the test cases, without changing code. The test code was run against our implementation outside the repository before it was added.
- Expected results we defined ourselves:
  - For the demo forecast the peak is 42.0°C at 15:00 with the expected level `danger`.
  - When the weather data is unavailable, every weather field in the report is empty, `data_source` is `unavailable` and nobody is counted as flagged.
- What we verified: ran `python -m pytest -v` (123 tests passed), including a check that the Stage 1 waiting report still counts only waiting patients.
- What we decided: the forecast uses the same `classify_heat_level` rule as the current decision. The flagged patients are counted from the patients themselves, so a patient who started treatment is not counted. `data_source` is taken from the weather snapshot, so simulated data cannot appear as live data.

### T14 – Main integration

- Tool: OpenAI Codex (OpenAI), used to help implement the integration, write tests and review the code against our requirements.
- The tool first proposed the integration plan and the test cases, without changing code. We reviewed and approved the plan before implementation, keeping the existing interfaces and the Stage 1 behaviour.
- Expected results we defined ourselves:
  - The offline demo flags exactly `P005` and `P011`, records the reason `heat:danger`, and reports a forecast maximum of 42.0°C.
  - When the weather client fails, nobody is flagged and the report is `unavailable`, without falling back to simulated weather. Urgency levels and the clinical queue order stay unchanged.
- What we verified: ran the full test suite in PowerShell (131 tests passed) and completed the offline demonstration successfully. The tests cover the report, audit log, nurse worklist, output order and client selection; the live client is mocked, so no real LIVE execution was verified at this stage.
- What we corrected: after reviewing the code review findings, we requested tests for the entry points and the absence of fallback, a worklist sorting test with unsorted input and different urgency levels, and a clear message when the Threads demo has no patients to claim.
- What we decided: all dependencies are connected in `main.py`, and Stage 2 loads its own patients so the Stage 1 demonstration cannot change its results. Offline is the default; only `--live` selects Open-Meteo. Lab results and nurse claims are marked as simulated, and an empty worklist does not cause extra patients to be created.

### T15 – Live verification

- Tool: OpenAI Codex (OpenAI), used to help plan the verification and document the results supplied by the team.
- The tool first proposed the command, the expected output and the evidence to keep, without changing code. We performed the real execution ourselves and supplied the results for documentation.
- Expected results we defined ourselves:
  - A successful real request is marked as LIVE with status `applied`, and shows the observation time, apparent temperature, heat level and forecast maximum.
  - An apparent temperature below 32°C gives level `normal` and flags nobody.
- What we verified: ran `python main.py --live` on 2026-11-02 at 18:52:19 +02:00. Open-Meteo returned status `applied`, observation time `2026-11-02T18:45`, apparent temperature 27.3°C, forecast maximum 28.5°C, heat level `normal` and 0 flagged patients. This was the team's real LIVE run, not a mocked test or an execution by the tool.
- What we decided: T15 needed no application or test changes. We kept the supplied LIVE evidence in `docs/T15_LIVE_VERIFICATION.md` for inclusion in the Stage 2 README during T16, separately from the simulated demonstrations.

### T16 – Stage 2 README documentation

- Tool: OpenAI Codex (OpenAI), used to help organize and write the Stage 2 documentation against our work plan and existing code.
- The tool first proposed the README content, the documentation to preserve and the checks to perform, without changing files. We reviewed and approved the plan before the documentation was updated.
- Expected results we defined ourselves:
  - One Stage 2 section explains setup, architecture, rules, error handling and verification without repeating the Stage 1 explanations.
  - The README preserves our exact T15 LIVE results and links to the three real `classify_heat_level` TDD commits, without inventing console output or commit references.
- What we verified: the documentation was checked against the existing implementation, settings, work plan and saved T15 record. The tool checked the TDD hashes in Git history, local documentation links, the single Stage 2 heading and `git diff --check`. The 131 passing tests and the offline and LIVE runs are our earlier verification results; no tests or LIVE requests were rerun for this documentation task.
- What we decided: keep the Stage 1 documentation, correct the outdated dependency statement, and put the Stage 2 additions in one section. AI usage stays in this file, and the saved T15 evidence remains unchanged.

### T17 – Final AI documentation review

- Tool: OpenAI Codex (OpenAI), used to help review the AI usage record against the work plan and Git history and make the documentation corrections we approved.
- The tool first reported the coverage gaps, attribution issues and proposed corrections, without changing files. We reviewed and approved the plan, requiring that missing historical details be stated rather than invented.
- Expected results we defined ourselves:
  - The record covers T0–T17, acknowledges AI assistance with the work plan, and preserves the team's ownership of requirements, decisions, review and final approval.
  - Tool assistance, team verification and historical uncertainties are distinguished without adding unsupported approvals, test results or LIVE executions.
- What we verified: reviewed the full AI usage record and work plan against Git history, checked task headings for T0–T17 coverage and duplicates, and ran `git diff --check`. These are documentation checks; no tests or LIVE requests were run, and earlier reported results were not independently reverified.
- What we corrected: expanded the opening tool summary, replaced the blanket validation claim with task-specific attribution, acknowledged the AI-assisted work plan, added an evidence-based T0 entry, and clarified that the T8 and T14 statements describe their respective stages.
- What we decided: preserve the existing historical task reports and their tool attribution, explicitly record T0's evidence limits, and leave T18 pending until the final submission checks are performed.

### T18 – Final validation

- Tool: OpenAI Codex (OpenAI), used to help plan the final checks, audit tracked files and documentation, and record the results supplied by the team.
- The tool first proposed the validation plan without changing files or running tests. We performed the clean-clone validation ourselves and approved documentation updates after the read-only audit.
- Expected results we defined ourselves:
  - A fresh installation and the full test suite succeed in a clean clone; the default demonstration works with the internet disconnected and flags exactly `P005` and `P011` at level `danger`, with forecast maximum 42.0°C.
  - A real LIVE run reports Open-Meteo data with status `applied`, while tracked files contain no accidental secrets or caches and preserve the three TDD commits.
- What we verified: in a clean clone at `49c2819`, we completed a fresh installation and obtained `131 passed in 2.46s`, followed by `131 passed in 2.14s`. With the internet physically disconnected, we obtained `131 passed in 2.15s` and a successful default run with SIMULATED source, level `danger`, and `P005` and `P011` flagged. Our LIVE run at 2026-11-02 19:13:47 +02:00 returned Open-Meteo data with status `applied`, observation time `2026-11-02T19:00`, apparent temperature and forecast maximum both 26.9°C, level `normal` and 0 flagged patients. These executions and the disconnection confirmation were supplied by us; Codex did not independently execute or observe them.
- What we corrected: replaced the README's earlier incomplete test summary with the supplied T18 results and kept the new LIVE record separate from the unchanged T15 evidence. Codex's read-only audit checked Git status and diffs, tracked-file names and common credential patterns, README commands and local links, TDD history and AI usage coverage; documentation checks included `git diff --check`.
- What we decided: record technical validation as complete without treating the final peer review, integration merge, team module explanations or submission as completed. No application code or tests were changed for this documentation task.
