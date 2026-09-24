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
  "arrival_time": "2026-09-16T18:00:00",
  "status": "waiting",
  "assessment": {
    "chief_complaint": "Chest pain",
    "pain_level": 8,
    "urgency_level": 1
  }
}