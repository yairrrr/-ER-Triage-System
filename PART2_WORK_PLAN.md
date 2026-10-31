# תכנית עבודה – שלב 2

מערכת ER Triage – שירות חיצוני, תבניות תכנון, בדיקות ומקביליות.

אנחנו שלישייה, ולכן סעיף 6 במסמך ההוראות (רביעייה) לא רלוונטי לנו.

---

## איך עובדים עם המסמך

אין תפקידים קבועים. יש רשימת משימות (סעיף 2), וכל אחד לוקח משימה פנויה כשנוח לו.

נוהל לקיחת משימה:

- [ ] בוחרים משימה שכל המשימות שהיא תלויה בהן כבר מוזגו ל־`main`.
- [ ] כותבים בקבוצת הווטסאפ: "לוקח את T7". מי שכתב ראשון – שלו.
- [ ] פותחים ענף בשם שמופיע במשימה, מ־`main` מעודכן.
- [ ] מסיימים, מריצים `python -m pytest`, פותחים PR, ומישהו אחר מאשר.
- [ ] אחרי המיזוג כותבים בווטסאפ: "T7 מוזג".
- [ ] מוסיפים ל־`AI_USAGE.md` שורות על המשימה (ראו T17).

כשמעבירים משימה ל־AI, מעבירים תמיד **את סעיף 0 במלואו + המשימה עצמה**. סעיף 0 הוא החוזה המשותף, וככה כל ה־AI-ים עובדים עם אותם שמות, חתימות וכללים.

הנחיה קבועה שמדביקים ל־AI בתחילת כל משימה (נדרש בסעיף 7.3 במטלה):

```text
לפני שאתה משנה קוד: הצג תוכנית קצרה ורשימת מקרי בדיקה, וחכה לאישור שלי.
עבוד רק לפי החוזה בסעיף 0. אם משהו לא מוגדר שם – שאל אותי, אל תמציא.
אל תשנה תוצאה צפויה בבדיקה רק כדי שהבדיקה תעבור.
אחרי השינוי הרץ את כל הבדיקות (python -m pytest), לא רק את החדשות.
אל תשנה קבצים שלא מופיעים במשימה.
```

---

## 0. החוזה המשותף (מחייב את כולם)

### 0.1 ההרחבה העסקית

התהליך שמרחיבים: ניהול המטופלים הממתינים בחדר המיון.

הרעיון: **התרעת עומס חום**. המערכת שולפת משירות מזג אוויר אמיתי את הטמפרטורה המורגשת הנוכחית ואת התחזית לשש השעות הקרובות.

לפי הטמפרטורה הנוכחית היא קובעת רמת עומס חום. בהתאם לרמה היא מסמנת מטופלים ממתינים בקבוצת סיכון כ"צריכים הערכה מחדש", ומכניסה אותם לרשימת עבודה לאחות.

המערכת **לא משנה דחיפות ולא משנה את סדר התור**. היא רק מסמנת ומדווחת, והאחות מחליטה.

הדוח מציג את רמת החום, את המקסימום הצפוי בתחזית, ואת המטופלים המסומנים.

הערך העסקי: מטופלים פגיעים לחום לא "נעלמים" בהמתנה ארוכה, והצוות מקבל רשימה ממוקדת של מי לבדוק שוב.

### 0.2 השירות החיצוני (נבדק בפועל ב־29.10.2026)

Open-Meteo Forecast API – חינמי, ללא מפתח.

תיעוד: https://open-meteo.com/en/docs

הבקשה, אחת בלבד, מחזירה גם מצב נוכחי וגם תחזית:

```text
GET https://api.open-meteo.com/v1/forecast
params:
  latitude=32.0853
  longitude=34.7818
  current=temperature_2m,apparent_temperature,relative_humidity_2m
  hourly=apparent_temperature
  forecast_hours=6
  timezone=auto
timeout=5
```

תגובה אמיתית שהתקבלה (קוד 200), מקוצרת:

```json
{
  "current": {"time": "2026-10-29T20:15", "interval": 900,
              "temperature_2m": 22.7, "apparent_temperature": 24.0,
              "relative_humidity_2m": 68},
  "hourly": {"time": ["2026-10-29T20:00", "2026-10-29T21:00", "..."],
             "apparent_temperature": [23.9, 23.5, "..."]}
}
```

תגובה לפרמטר לא תקין (קוד 400), נבדק בפועל:

```json
{"reason": "Latitude must be in range of -90 to 90°. Given: 999.0.", "error": true}
```

שדות שחובה לאמת:

```text
current                       dict
current.time                  str
current.temperature_2m        מספר (int/float, לא bool), בטווח -60..60
current.apparent_temperature  מספר, בטווח -60..60
current.relative_humidity_2m  מספר, בטווח 0..100
hourly                        dict
hourly.time                   רשימה לא ריקה של str
hourly.apparent_temperature   רשימה של מספרים, באותו אורך כמו hourly.time
```

### 0.3 כללים עסקיים (מכאן נקבעות כל התוצאות הצפויות)

רמת עומס חום, לפי הטמפרטורה המורגשת **הנוכחית**:

```text
apparent < 32           -> "normal"
32 <= apparent < 39     -> "caution"
apparent >= 39          -> "danger"
```

מקור הספים: קטגוריות ה־Heat Index של שירות המטאורולוגיה האמריקאי (NWS). הטמפרטורה המורגשת של Open-Meteo מחושבת בנוסחה אחרת, ולכן השימוש בספים הוא קירוב והנחה של הפרויקט. כך זה ייכתב גם ב־README.

תלונה רגישה לחום – `chief_complaint` מכיל, בלי הבדל בין אותיות גדולות לקטנות, אחת מהמחרוזות:

```text
"dizz", "weak", "confus", "breath", "fever"
```

מטופל מתאים לבדיקה רק אם הוא בסטטוס `waiting`, ברמת דחיפות גדולה מ־1, ועדיין לא מסומן.

מי מסומן בכל רמה:

```text
normal   -> אף אחד
caution  -> רק מי שגם age >= 65 וגם תלונה רגישה לחום   ("פגיעים")
danger   -> כל מי שאו age >= 65 או תלונה רגישה לחום   ("קבוצת סיכון")
```

הסימון יורד כשהמטופל מתחיל טיפול.

בכשל של השירות (תקשורת אחרי 3 ניסיונות, HTTP, JSON פגום, שדה חסר או לא תקין):

- אף מטופל לא מסומן ושום דבר לא משתנה.
- לא משתמשים בנתונים מדומים במקום הנתונים האמיתיים.
- נכתב `logging.warning` עם סוג הכשל.
- הדוח מציין שנתוני מזג האוויר לא זמינים.

תוצאות צפויות על `data/sample_data.jsonl` שהקבוצה קבעה בעצמה (לתיעוד ב־`AI_USAGE.md`):

```text
danger  (למשל 40):  מסומנים בדיוק P005, P011
caution (למשל 35):  מסומן רק P011
כשל תקשורת:         3 קריאות לשירות, 2 המתנות, אף אחד לא מסומן, הדוח "unavailable"
```

הסבר: P001, P004, P008, P013 ברמת דחיפות 1 ולכן לא מסומנים. P005 בן 52 עם fever, ולכן מסומן רק בסכנה. P011 בן 72 עם dizziness, ולכן מסומן בשתי הרמות.

### 0.4 שמות, קבצים וחתימות

החבילה נשארת `er_triage` (במטלה כתוב `project_name`).

```text
er_triage/config.py              הגדרות ממשתני סביבה
er_triage/api_client.py          תקשורת עם השירות + אימות + Retry
er_triage/strategies.py          Strategy – כללי סימון
er_triage/observers.py           Observer – אירוע סימון ומגיבים
er_triage/services.py            השירות העסקי שמחבר הכול
er_triage/async_processing.py    איסוף תוצאות מעבדה (סימולציה)
er_triage/threaded_processing.py אחיות שמושכות מרשימת העבודה במקביל
er_triage/reporting.py           פונקציית דוח חדשה (הקיימת לא משתנה)
er_triage/models.py              שדות סימון ב-Patient + WeatherSnapshot
data/weather_sample.json         תגובה לדוגמה במצב בלי רשת (סכנה)
data/lab_results.json            נתוני מעבדה מדומים
.env.example                     שמות משתנים וערכי דוגמה בלבד
```

#### models.py

```python
@dataclass(frozen=True)
class HourlyForecast:
    time: str
    apparent_temperature_c: float

@dataclass(frozen=True)
class WeatherSnapshot:
    observed_at: str
    temperature_c: float
    apparent_temperature_c: float
    humidity_percent: float
    forecast: tuple[HourlyForecast, ...]
    source: str                      # "live" או "simulated"
```

שינויים ב־`Patient` (חייבים להשאיר את כל ההתנהגות של שלב 1):

```python
# שדות חדשים, עם ערכי ברירת מחדל כדי שטעינת שלב 1 תמשיך לעבוד:
#   self.needs_reassessment = False
#   self.reassessment_reason = None

def flag_for_reassessment(self, reason): ...   # מסמן ושומר סיבה, למשל "heat:danger"; ValueError אם לא waiting
def start_treatment(self): ...                  # כמו היום + מוריד את הסימון
```

#### api_client.py

```python
class WeatherServiceError(Exception): ...               # בסיס – זה מה ש-services תופס
class WeatherConnectionError(WeatherServiceError): ...  # Timeout/ConnectionError אחרי 3 ניסיונות
class WeatherHTTPError(WeatherServiceError): ...        # raise_for_status נכשל – בלי Retry
class WeatherDataError(WeatherServiceError): ...        # JSON פגום / שדה חסר / ערך לא תקין – בלי Retry

def parse_weather_payload(payload: dict, source: str) -> WeatherSnapshot: ...

class OpenMeteoClient:
    def __init__(self, session, base_url, latitude, longitude, timeout,
                 max_attempts=3, base_delay=1.0, sleep=time.sleep): ...
    def get_weather(self) -> WeatherSnapshot: ...           # source="live"

class OfflineWeatherClient:
    def __init__(self, file_path): ...
    def get_weather(self) -> WeatherSnapshot: ...           # source="simulated"
```

`session` הוא אובייקט עם מתודה `get`. במצב אמיתי מעבירים `requests.Session()`, ובבדיקות מעבירים `Mock`.

`sleep` מוזרק כדי שהבדיקות לא יחכו באמת.

Retry: ההמתנה מתארכת – `base_delay * 2 ** (attempt - 1)`, כלומר שנייה ואחר כך שתי שניות. אין המתנה אחרי הניסיון האחרון.

#### strategies.py

```python
class FlaggingStrategy(ABC):
    def eligible(self, patient) -> bool: ...        # waiting, urgency > 1, לא מסומן כבר
    @abstractmethod
    def select(self, patients) -> list: ...          # מחזיר את המטופלים לסימון

class NoFlaggingStrategy(FlaggingStrategy): ...      # normal – תמיד רשימה ריקה
class VulnerableOnlyStrategy(FlaggingStrategy): ...  # caution – גיל וגם תלונה
class AllAtRiskStrategy(FlaggingStrategy): ...       # danger – גיל או תלונה

def is_heat_sensitive(patient) -> bool: ...
```

#### observers.py

```python
@dataclass(frozen=True)
class PatientFlaggedEvent:
    patient: Patient
    heat_level: str

class EventPublisher:
    def subscribe(self, observer): ...
    def publish(self, event): ...        # קורא ל-observer.notify(event) לכל מנוי, לפי סדר ההרשמה

class AuditLogObserver:
    # notify: logging.info עם patient_id ורמת החום (בלי שם!), ושומר מחרוזת ב-self.entries

class ReassessmentWorklist:
    # notify: מוסיף את המטופל לרשימה
    def pending(self) -> list: ...       # מטופלים שעדיין מסומנים, לפי (urgency_level, arrival_time)
    def claim_next(self, nurse_id): ...  # מחזיר מטופל אחד ומסיר אותו, או None. מוגן ב-Lock (T12)
```

#### services.py

```python
def classify_heat_level(apparent_temperature_c) -> str: ...   # מפותח ב-TDD (T6)
def summarize_forecast(forecast) -> dict: ...                  # max, time, expected level

@dataclass
class HeatCheckResult:
    status: str                  # "applied" או "unavailable"
    heat_level: str | None
    snapshot: WeatherSnapshot | None
    flagged_patient_ids: list[str]
    error_message: str | None

class HeatAlertService:
    def __init__(self, weather_client, publisher, strategies): ...
    # strategies: dict {"normal": ..., "caution": ..., "danger": ...} – מוזרק מבחוץ
    def run_check(self, patients) -> HeatCheckResult: ...
```

`run_check` לא מכיל `if` על רמת החום. הוא שולף את האסטרטגיה מהמילון לפי הרמה ומפעיל אותה.

#### async_processing.py

```python
@dataclass(frozen=True)
class LabResult:
    patient_id: str
    test_name: str
    value: float
    is_critical: bool

def load_lab_data(file_path) -> dict: ...
async def fetch_lab_result(patient_id, lab_data, delays) -> LabResult: ...
async def collect_lab_results_sequential(patient_ids, lab_data, delays) -> list[LabResult]: ...
async def collect_lab_results_concurrent(patient_ids, lab_data, delays) -> list[LabResult]: ...
def find_critical_patients(results) -> list[str]: ...
```

#### threaded_processing.py

```python
def nurses_claim_concurrently(worklist, nurse_ids) -> dict: ...
# Thread לכל אחות. כל אחות מושכת claim_next עד שהרשימה ריקה.
# מחזיר {nurse_id: [patient_id, ...]}
```

### 0.5 Git

- ענף לכל משימה, בשם שמופיע במשימה.
- נכנסים ל־`main` רק דרך PR, וחבר אחר עובר על ה־PR.
- מיזוג עם **Create a merge commit** בלבד. בלי Squash – אחרת שלושת commits ה־TDD נמחקים.
- אסור להעלות `.env` או מפתחות.

### 0.6 סגנון

לשמור על הסגנון של שלב 1: מחלקות פשוטות, שמות באנגלית, בלי ספריות מיותרות.

כל מודול שמתעד משתמש ב־`logging.getLogger(__name__)`. רק `main.py` מגדיר `logging.basicConfig`.

בלוגים רק `patient_id`, אף פעם לא שם (מידע אישי).

אין `print` בתוך החבילה – רק ב־`main.py`.

### 0.7 החלטות קטנות שקבעתי בעצמי (אפשר לשנות)

אלה ערכי ברירת מחדל ולא החלטות שקיבלנו יחד. אם מישהו רוצה לשנות – בווטסאפ, לפני שמתחילים את המשימה הרלוונטית.

```text
מיקום בית החולים:     32.0853, 34.7818 (תל אביב)
timeout:              5 שניות
המתנות Retry:          1 ואז 2 שניות
שעות תחזית:            6
דגל הפעלה אמיתית:      python main.py --live
תוצאה צפויה בדוגמה:   קובץ weather_sample.json עם apparent 40.5 (סכנה), ומקסימום תחזית 42.0
```

---

## 1. סדר התלויות

```text
T0 ─┬─ T1 ──────────────┐
    ├─ T2 ─┬─ T3 ───────┤
    │      └─ T4 ───────┤
    ├─ T5 ─┬─ T7 ─┐     │
    │      └─ T8 ─┼─ T9 ─ T10 ─┐
    ├─ T6 ────────┘     │      │
    │         T8 ─ T12 ─┤      ├─ T14 ─ T15 ─ T16 ─ T18
    ├─ T11 ─────────────┘      │
    └─ T13 ────────────────────┘
T17 – כל אחד, אחרי כל משימה שלו
```

אחרי T0 אפשר להתחיל במקביל: T1, T2, T5, T6, T11, T13.

T9 צריך את T2, T6, T7, T8. אם T2 עוד לא מוזג, אפשר לעבוד מול החוזה עם לקוח מזויף, אבל ה־PR נכנס רק אחרי T2.

---

## 2. רשימת המשימות

### T0 – הכנת המאגר

**ענף:** `task/T0-setup` | **תלוי ב:** כלום – חייבת להיות ראשונה

- [x] למזג את הענף `fix/lecturer-feedback` ל־`main` (תיקוני המרצה לשלב 1) – כבר בוצע, `main` מכיל את commit `17bb727`.
- [ ] לעדכן את `pyproject.toml` (למטה).
- [ ] ליצור `tests/__init__.py` ריק ו־`tests/conftest.py` (למטה).
- [x] להוסיף את הקובץ הזה למאגר.
- [ ] לוודא שהפקודות `pip install -e ".[dev]"`, `python -m pytest` ו־`python main.py` עובדות.

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "er-triage-system"
version = "0.2.0"
description = "Emergency room patient triage and priority queue management system"
requires-python = ">=3.11"
dependencies = ["requests>=2.31", "python-dotenv>=1.0"]

[project.optional-dependencies]
dev = ["pytest>=8.0"]

[tool.setuptools]
packages = ["er_triage"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

```python
# tests/conftest.py
from datetime import date, datetime, time

import pytest
from er_triage.models import Patient, TriageAssessment


def today_at(hour, minute=0):
    return datetime.combine(date.today(), time(hour, minute)).isoformat()


def make_patient(patient_id, age, complaint, urgency, status="waiting",
                 arrival_time=None, pain=5):
    if arrival_time is None:
        arrival_time = today_at(6)
    return Patient(patient_id, f"Test {patient_id}", age, arrival_time,
                   TriageAssessment(complaint, pain, urgency), status)


@pytest.fixture
def heat_patients():
    return [
        make_patient("H001", 72, "Dizziness", 3),                      # גיל + תלונה
        make_patient("H002", 52, "High fever", 3),                     # תלונה בלבד
        make_patient("H003", 70, "Broken wrist", 4),                   # גיל בלבד
        make_patient("H004", 25, "Ankle injury", 4),                   # לא בסיכון
        make_patient("H005", 80, "Difficulty breathing", 1),           # דחיפות 1
        make_patient("H006", 68, "Weakness", 2, status="in_treatment"),# לא ממתין
    ]
```

מותר להוסיף fixtures לקובץ. לשנות קיים רק בתיאום בווטסאפ.

חשוב לכל המשימות: זמן הגעה תקין הוא רק תאריך של היום (תיקון הערת המרצה, בוצע ב־T0). בבדיקות לא כותבים תאריך קבוע – משתמשים ב־`today_at(hour, minute)`. בקובץ JSONL של נתונים, `arrival_time` הוא שעה בלבד, למשל `"06:00:00"`, והטעינה מוסיפה את התאריך של היום.

---

### T1 – הגדרות וסודות

**ענף:** `task/T1-config` | **תלוי ב:** T0 | **סעיף במטלה:** 2.3

- [ ] `er_triage/config.py`: קורא ל־`load_dotenv()`, ואחר כך קורא משתני סביבה עם ברירות מחדל וממיר לטיפוס הנכון.
- [ ] `.env.example` בשורש: אותם שמות עם ערכי דוגמה.
- [ ] לוודא ש־`.env` מופיע ב־`.gitignore` (כבר קיים – רק לבדוק).

```text
WEATHER_API_URL          https://api.open-meteo.com/v1/forecast
HOSPITAL_LATITUDE        32.0853
HOSPITAL_LONGITUDE       34.7818
WEATHER_TIMEOUT_SECONDS  5
WEATHER_MAX_ATTEMPTS     3
WEATHER_BASE_DELAY       1.0
WEATHER_FORECAST_HOURS   6
WEATHER_SAMPLE_FILE      data/weather_sample.json
LOG_LEVEL                INFO
```

ערך שלא ניתן להמרה גורם ל־`ValueError` עם שם המשתנה.

לשירות שלנו אין מפתח. `.env.example` קיים כדי להראות את מנגנון ההגדרות שהמטלה דורשת.

**סיום:** אין URL, קואורדינטות או timeout קשיחים בשום מקום אחר בקוד.

---

### T2 – מודל מזג האוויר ואימות התגובה

**ענף:** `task/T2-weather-parsing` | **תלוי ב:** T0 | **סעיף במטלה:** 2.1

- [ ] להוסיף ל־`models.py` את `HourlyForecast` ו־`WeatherSnapshot` בדיוק לפי 0.4.
- [ ] ליצור את `api_client.py` עם ארבע החריגות ועם `parse_weather_payload(payload, source)`.
- [ ] `parse_weather_payload` מאמת כל שדה ב־0.2: קיום, טיפוס (bool נדחה), טווח, ואורך שווה של שתי רשימות התחזית.
- [ ] כל כשל אימות זורק `WeatherDataError` עם שם השדה הבעייתי.
- [ ] בלי רשת ובלי מטופלים – רק נתונים פנימה ואובייקט החוצה.

בדיקות ב־`tests/test_api_client.py`:

- [ ] תגובה תקינה (מבוססת על התגובה האמיתית ב־0.2) מחזירה את הערכים הנכונים ושש שעות תחזית.
- [ ] `parametrize` עם לפחות 5 שורות: חסר `current`; חסר `apparent_temperature`; ערך `"hot"`; ערך `True`; ערך 500; רשימות תחזית באורך שונה. בכולן `pytest.raises(WeatherDataError)`.

---

### T3 – בקשת ה־GET, שגיאות ו־Retry

**ענף:** `task/T3-open-meteo-client` | **תלוי ב:** T1, T2 | **סעיפים במטלה:** 2.1, 2.2, 2.3

`OpenMeteoClient.get_weather()`, לפי הסדר:

- [ ] בונה את הפרמטרים מ־0.2, עם ערכים מ־config.
- [ ] קורא `self.session.get(url, params=..., timeout=self.timeout)`.
- [ ] על `requests.Timeout` או `requests.ConnectionError`: `logger.warning` עם מספר הניסיון, `self.sleep(delay)` מתארך, וניסיון נוסף. עד 3 ניסיונות **בסך הכול**.
- [ ] אחרי הניסיון השלישי: `raise WeatherConnectionError(...) from error` עם הודעה ברורה.
- [ ] `response.raise_for_status()`. `requests.HTTPError` הופך ל־`WeatherHTTPError` עם קוד הסטטוס. **בלי Retry**, גם על 401 ו־403.
- [ ] `response.json()`. `ValueError` הופך ל־`WeatherDataError`. בלי Retry.
- [ ] `parse_weather_payload(payload, "live")`.
- [ ] `logger.info` בהצלחה: טמפרטורה וזמן בלבד.

טיפול מיוחד ב־429 או 503 – רשות. לא מתוכנן.

הלקוח לא יודע כלום על מטופלים או על רמות חום.

בדיקות ב־`tests/test_api_client.py` – עם `session=Mock()` ו־`sleep=Mock()`, בלי רשת:

- [ ] הצלחה: הוחזר snapshot עם `source="live"`, ו־`session.get` נקרא עם `params` ו־`timeout`.
- [ ] Timeout ואז הצלחה: מצליח, `session.get` נקרא פעמיים, `sleep` נקרא פעם אחת עם 1.
- [ ] מיצוי: שלוש פעמים `ConnectionError` זורק `WeatherConnectionError`, `session.get` נקרא 3 פעמים, ו־`sleep` נקרא בדיוק עם 1 ואז 2.
- [ ] HTTP 500 זורק `WeatherHTTPError`, ו־`session.get` נקרא פעם אחת.
- [ ] HTTP 401 זורק `WeatherHTTPError`, ו־`session.get` נקרא פעם אחת.
- [ ] JSON פגום (`response.json` זורק `ValueError`) זורק `WeatherDataError`, עם קריאה אחת.
- [ ] שדה חסר בתגובה זורק `WeatherDataError`, עם קריאה אחת.

---

### T4 – לקוח בלי רשת ונתוני הדגמה

**ענף:** `task/T4-offline-client` | **תלוי ב:** T2 | **סעיפים במטלה:** 7.1, 4.1 (tmp_path)

- [ ] `data/weather_sample.json`: אותו מבנה בדיוק כמו התגובה האמיתית. `apparent_temperature` נוכחי 40.5, ושש שעות תחזית עם מקסימום 42.0.
- [ ] `OfflineWeatherClient(file_path).get_weather()` קורא את הקובץ ומשתמש ב־`parse_weather_payload(payload, "simulated")`.
- [ ] קובץ חסר או JSON פגום זורקים `WeatherDataError`.

בדיקות עם `tmp_path`:

- [ ] קובץ תקין מחזיר `source="simulated"` ואת הערכים מהקובץ.
- [ ] קובץ פגום זורק `WeatherDataError`.

---

### T5 – סימון במטופל

**ענף:** `task/T5-patient-flag` | **תלוי ב:** T0

- [ ] להוסיף ל־`Patient` את `needs_reassessment=False` ו־`reassessment_reason=None`.
- [ ] `flag_for_reassessment(reason)` מסמן ושומר סיבה. מטופל שאינו בסטטוס `waiting` נדחה עם `ValueError` (הוחלט בקבוצה).
- [ ] `start_treatment()` ממשיך לשנות סטטוס כמו היום, ובנוסף מוריד את הסימון ומאפס את הסיבה.
- [ ] `patient_from_dict` וטעינת `sample_data.jsonl` עובדים בלי שינוי בקובץ הנתונים.

בדיקות ב־`tests/test_models.py`:

- [ ] מטופל חדש לא מסומן.
- [ ] אחרי `flag_for_reassessment("heat:danger")` הוא מסומן עם הסיבה.
- [ ] אחרי `start_treatment()` הסטטוס `in_treatment` והסימון ירד.

---

### T6 – סיווג רמת החום ב־TDD

**ענף:** `task/T6-tdd-heat-level` | **תלוי ב:** T0 | **סעיף במטלה:** 4.2

שלושה commits נפרדים, בדיוק עם ההודעות האלה:

**Commit 1:**

```text
TDD Red: add failing tests for classify_heat_level
```

- [ ] ב־`services.py`: שלד של `classify_heat_level` שמחזיר תמיד `"normal"`.
- [ ] ב־`tests/test_services.py`: `parametrize` עם הערכים 20 ל־normal, 31.9 ל־normal, 32 ל־caution, 38.9 ל־caution, 39 ל־danger, 45 ל־danger.
- [ ] להריץ ולוודא שהבדיקות נכשלות **על assertion** ולא על ImportError. לשמור את שורת הסיכום ל־README.

**Commit 2:**

```text
TDD Green: implement classify_heat_level thresholds
```

- [ ] מימוש מינימלי. כל הבדיקות עוברות.

**Commit 3:**

```text
TDD Refactor: extract heat thresholds into named constants
```

- [ ] להעביר את 32 ו־39 לקבועים בעלי שם בראש הקובץ, ולהוסיף docstring קצר עם מקור הספים.
- [ ] כל הבדיקות עוברות.

לא מאחדים את שלושת ה־commits.

---

### T7 – Strategy: כללי הסימון

**ענף:** `task/T7-flagging-strategies` | **תלוי ב:** T5 | **סעיף במטלה:** 3

- [ ] `strategies.py` לפי 0.4: `is_heat_sensitive`, `FlaggingStrategy` עם `eligible` משותף, ושלוש אסטרטגיות.
- [ ] המחרוזות של התלונות הרגישות הן קבוע אחד בראש הקובץ.
- [ ] אין בדיקות סוג (`isinstance`) בקוד העסקי.

בדיקות ב־`tests/test_strategies.py` עם ה־fixture `heat_patients`:

- [ ] `NoFlaggingStrategy` מחזירה רשימה ריקה.
- [ ] `VulnerableOnlyStrategy` מחזירה בדיוק את H001.
- [ ] `AllAtRiskStrategy` מחזירה בדיוק את H001, H002, H003.
- [ ] `parametrize` על `is_heat_sensitive`: "Dizziness", "SHORTNESS OF BREATH", "General weakness" מחזירים True; "Ankle injury" מחזיר False.
- [ ] מטופל שכבר מסומן לא מוחזר שוב.

---

### T8 – Observer: אירוע הסימון

**ענף:** `task/T8-observers` | **תלוי ב:** T5 | **סעיף במטלה:** 3

- [ ] `observers.py` לפי 0.4: `PatientFlaggedEvent`, `EventPublisher`, `AuditLogObserver`, `ReassessmentWorklist`. בשלב הזה בלי Lock – הוא נוסף ב־T12.
- [ ] `ReassessmentWorklist.pending()` מחזיר רק מטופלים שעדיין מסומנים, ממוינים לפי דחיפות ואז זמן הגעה.
- [ ] `claim_next(nurse_id)` מסיר ומחזיר את הראשון ב־`pending`, או `None` אם אין.

בדיקות ב־`tests/test_observers.py`:

- [ ] `publish` אחד מפעיל את שני המגיבים: ביומן רשומה אחת, וברשימה מטופל אחד.
- [ ] ביומן מופיע ה־`patient_id` ולא שם המטופל.
- [ ] `pending` ממוין: מטופל ברמה 2 לפני מטופל ברמה 3.
- [ ] מטופל שהתחיל טיפול כבר לא מופיע ב־`pending`.
- [ ] `claim_next` על רשימה ריקה מחזיר `None`.

---

### T9 – השירות העסקי

**ענף:** `task/T9-heat-alert-service` | **תלוי ב:** T2, T6, T7, T8 | **סעיפים במטלה:** 1, 2.1, 2.2, 3

`HeatAlertService.run_check(patients)`:

- [ ] קורא `self.weather_client.get_weather()` בתוך `try`, ותופס רק `WeatherServiceError`.
- [ ] בכשל: `logger.warning`, ומחזיר `HeatCheckResult(status="unavailable", ...)` בלי לגעת באף מטופל.
- [ ] בהצלחה: `classify_heat_level`, ואז האסטרטגיה מהמילון לפי הרמה, ואז `select`.
- [ ] לכל מטופל שנבחר: `patient.flag_for_reassessment(f"heat:{level}")`, ואחר כך `publisher.publish(PatientFlaggedEvent(...))`.
- [ ] מחזיר `status="applied"` עם רשימת המזהים שסומנו.
- [ ] אין `if` על רמת החום.

בדיקות ב־`tests/test_services.py`, עם לקוח מזויף שמחזיר snapshot:

- [ ] סכנה (40): H001, H002, H003 מסומנים; H004, H005, H006 לא.
- [ ] זהירות (35): רק H001.
- [ ] רגיל (25): אף אחד, ו־`flagged_patient_ids == []`.
- [ ] כשל תקשורת (`side_effect=WeatherConnectionError`): `status == "unavailable"`, אף אחד לא מסומן, הרשימה של האחות ריקה.
- [ ] כשל נתונים (`side_effect=WeatherDataError`): אותה תוצאה.
- [ ] הרצה שנייה ברמת סכנה לא מסמנת שוב ולא מפרסמת אירועים כפולים.

---

### T10 – הדוח

**ענף:** `task/T10-heat-report` | **תלוי ב:** T9

- [ ] `summarize_forecast(forecast)` ב־`services.py` מחזיר את המקסימום, את השעה שלו, ואת הרמה הצפויה לפי `classify_heat_level`.
- [ ] ב־`reporting.py` להוסיף פונקציה חדשה. `generate_waiting_report` הקיימת לא משתנה.

```python
def generate_heat_report(patients, result) -> dict:
    # {
    #   "data_source": "live" / "simulated" / "unavailable",
    #   "heat_level": ... או None,
    #   "apparent_temperature_c": ... או None,
    #   "forecast_max_c": ..., "forecast_max_time": ..., "forecast_level": ...,  (None בכשל)
    #   "flagged_count": מספר הממתינים שמסומנים כרגע,
    #   "flagged_patient_ids": [...],
    # }
```

בדיקות ב־`tests/test_reporting.py`:

- [ ] `summarize_forecast` על תחזית ידועה מחזיר מקסימום, שעה ורמה נכונים.
- [ ] דוח במצב applied עם ערכים ידועים.
- [ ] דוח במצב unavailable: `data_source == "unavailable"`, `flagged_count == 0`, ושדות התחזית `None`.

---

### T11 – איסוף אסינכרוני של תוצאות מעבדה

**ענף:** `task/T11-async-lab-results` | **תלוי ב:** T0 | **סעיף במטלה:** 5.1

הרעיון: לפני סבב רופאים מבקשים תוצאות מעבדה של כמה מטופלים. כל בקשה עצמאית.

זו סימולציה: ההמתנה היא `await asyncio.sleep(delay)` והנתונים מגיעים מקובץ מקומי.

- [ ] `data/lab_results.json`: תוצאה לחמישה מטופלים לפחות מתוך `sample_data.jsonl`, לפחות שתיים קריטיות. נתונים בדיוניים.
- [ ] `async_processing.py` לפי 0.4.
- [ ] גרסה סדרתית: `await` על כל בקשה לפני הבאה.
- [ ] גרסה מקבילית: `asyncio.gather` על כל הבקשות. התוצאות לפי סדר הקלט.
- [ ] בלי `time.sleep` ובלי `requests` בתוך פונקציה `async`.
- [ ] לא מטפלים בכשל של משימה בודדת (רשות במטלה, הוחלט לא לממש).

בדיקות ב־`tests/test_async_processing.py` עם `asyncio.run`, בלי ספריות נוספות:

- [ ] שתי הגרסאות מחזירות תוצאות זהות.
- [ ] ההמתנות 0.15, 0.05, 0.10: התוצאות בסדר הקלט אף שסדר הסיום שונה.
- [ ] המקבילית מהירה מסכום ההמתנות (פחות מ־0.25 כשהסכום 0.30), והסדרתית לפחות כסכום ההמתנות.
- [ ] `find_critical_patients` מחזיר בדיוק את המזהים הקריטיים.
- [ ] `load_lab_data` עם `tmp_path`.

---

### T12 – Threads ו־Lock על רשימת העבודה

**ענף:** `task/T12-threaded-worklist` | **תלוי ב:** T8 | **סעיף במטלה:** 5.2

- [ ] להוסיף ל־`ReassessmentWorklist` מנעול `threading.Lock` אחד.
- [ ] `claim_next` עושה **בתוך `with self.lock:`** את כל הרצף: בדיקה שיש מטופל ממתין, בחירת הראשון, והסרתו.
- [ ] `threaded_processing.py`: `nurses_claim_concurrently` יוצר Thread לכל אחות, מפעיל את **כולם** ב־`start`, ורק אחר כך `join` לכולם.
- [ ] בלי קריאת רשת בתוך הקטע הנעול.

בדיקות ב־`tests/test_threaded_processing.py`:

- [ ] 5 מטופלים מסומנים ו־4 אחיות: בסך הכול נלקחו בדיוק 5, אף מטופל לא נלקח פעמיים, והרשימה ריקה.
- [ ] `parametrize` על (מטופלים, אחיות): (1, 6), (10, 3), (0, 4). מספר הנלקחים שווה למספר המטופלים, והרשימה ריקה.
- [ ] לא בודקים **איזו** אחות לקחה מה – רק כמה ומה המצב הסופי.

הסבר ל־README: בלי נעילה, אחות א' בודקת שיש מטופל ממתין, ואחות ב' בודקת באותו רגע ומקבלת אותה תשובה. שתיהן לוקחות את אותו מטופל, והוא נבדק פעמיים בזמן שמטופל אחר מחכה. ה־Lock הופך את הבדיקה וההסרה לפעולה אחת.

---

### T13 – בדיקות רגרסיה לשלב 1

**ענף:** `task/T13-stage1-regression` | **תלוי ב:** T0 | **סעיף במטלה:** 4.1

`tests/test_models.py`:

- [ ] `parametrize` על `pain_level` לא תקין: -1, 11, 2.5, True. כולם `ValueError`.
- [ ] `parametrize` על `urgency_level` לא תקין: 0, 6, "1". כולם `ValueError`.
- [ ] `arrival_time` לא תקין זורק `ValueError`.
- [ ] `parametrize` על זמן הגעה שאינו היום: אתמול, מחר, `"2020-01-01T10:00:00"`. כולם `ValueError`; ו־`today_at(6)` מתקבל.
- [ ] `EmergencyQueue`: מטופל כפול זורק `ValueError`; `get_next_patient` מחזיר את הדחוף ביותר ומשנה סטטוס; תור ריק מחזיר `None`.
- [ ] עדכון דחיפות ממיין מחדש את התור.

`tests/test_repository.py` עם `tmp_path`:

- [ ] קובץ תקין עם שתי שורות (שעה בלבד, למשל `"06:00:00"`) מחזיר שני מטופלים, ותאריך ההגעה שלהם הוא היום.
- [ ] שעה לא תקינה בקובץ, למשל `"25:00:00"`, זורקת `ValueError` עם מספר השורה.
- [ ] JSON פגום זורק `ValueError` עם מספר השורה.
- [ ] שדה חסר זורק `ValueError`.
- [ ] מזהה כפול זורק `ValueError`.

---

### T14 – main.py ותהליך משולב

**ענף:** `task/T14-main-integration` | **תלוי ב:** T3, T4, T10, T11, T12, T13 | **סעיפים במטלה:** 3, 7.1, 4.1

- [ ] להעביר את ההדגמה הקיימת לפונקציה `run_stage1_demo()` בלי לשנות התנהגות.
- [ ] `argparse` עם הדגל `--live` בלבד. בלי תפריט.
- [ ] `logging.basicConfig(level=config.LOG_LEVEL)`.
- [ ] כל החיבורים נעשים ב־`main.py` (הזרקת תלויות): הלקוח, ה־publisher עם שני המגיבים, ומילון האסטרטגיות.

`run_stage2_demo(live)` מציג לפי הסדר:

- [ ] שורת מקור: `[DATA SOURCE: SIMULATED – data/weather_sample.json]` או `[DATA SOURCE: LIVE – Open-Meteo]`.
- [ ] רמת החום, מי סומן ולמה, ורשימת העבודה לאחות.
- [ ] הדוח.
- [ ] הדגמת כשל: לקוח שתמיד זורק `WeatherConnectionError`, והפלט מראה שאף אחד לא סומן.
- [ ] מקביליות `[SIMULATED]`: תוצאות מעבדה בסדרתי מול מקבילי עם זמנים, ואחיות שמושכות מהרשימה.

`python main.py` בלי דגל חייב לרוץ בלי רשת.

`tests/test_integration.py`:

- [ ] תהליך מלא עם `OfflineWeatherClient` אמיתי (קובץ ב־`tmp_path` ברמת סכנה), מטופלים, publisher ודוח. בודקים מי סומן, את רשימת האחות, את היומן ואת שדות הדוח.
- [ ] אותו תהליך עם לקוח שנכשל: אף אחד לא מסומן, והדוח unavailable.

---

### T15 – הוכחת חיבור אמיתי

**ענף:** אין (התוצאה נכנסת ב־T16) | **תלוי ב:** T14

- [ ] להריץ `python main.py --live` פעם אחת.
- [ ] לשמור קטע קצר מהפלט עם תאריך ושעה: זמן התצפית, הטמפרטורה המורגשת, הרמה, ומקסימום התחזית.
- [ ] אם השירות לא זמין לאורך זמן – פונים למרצה. **אסור** להציג את הקובץ המדומה כאילו הגיע מהרשת.

---

### T16 – README: הסעיף "שלב 2"

**ענף:** `task/T16-readme` | **תלוי ב:** כל משימות הקוד ו־T15 | **סעיף במטלה:** 7.2

מוסיפים ל־`README.md` כותרת אחת, `## Stage 2 (שלב 2)`, בלי לשכפל את שלב 1. קצר, בנקודות, כל נושא פעם אחת.

- [ ] **מה נוסף:** פסקה על התרעת עומס החום והערך העסקי.
- [ ] **איך מריצים:** Python 3.11 ומעלה, `pip install -e ".[dev]"`, הפניה ל־`.env.example`, ושלוש פקודות: `python main.py`, `python main.py --live`, `python -m pytest`.
- [ ] **ארגון הקוד:** עץ תיקיות מעודכן, ושורה לכל מודול חדש.
- [ ] **החלטות תכנון:** השירות וקישור לתיעוד; השדות שמאומתים; ארבעת סוגי הכשל; Retry ולמה אין Retry על נתונים או הרשאה; הכללים ומקור הספים; התגובה לכשל; Strategy ולמה; Observer ולמה; הזרקת תלויות וכיצד היא מאפשרת בדיקה בלי רשת; המשימות האסינכרוניות (סימולציה); המשאב המשותף ואיזו שגיאה ה־Lock מונע.
- [ ] **הוכחות:** שורת הסיכום של `pytest`; ההרצה האמיתית מ־T15; קישורים לשלושת commits ה־TDD עם ציון היכולת `classify_heat_level`.

תיעוד ה־AI לא נכנס ל־README.

---

### T17 – AI_USAGE.md (מתמשך)

**ענף:** יחד עם כל משימה | **סעיף במטלה:** 7.3

תחת כותרת `## Stage 2`, אחרי כל משימה מוסיפים:

```markdown
### T9 – Heat alert service (name)

- Tool: ...
- Asked first for a plan and test cases without code changes: yes – what it proposed
- Expected results we defined ourselves: (e.g. danger -> exactly P005, P011)
- What we verified: ...
- What we corrected or rejected: ...
```

- [ ] לפחות שתי תוצאות צפויות שהקבוצה קבעה (הן כבר מופיעות ב־0.3).
- [ ] לציין שהתכנית הזו הוכנה בעזרת AI, וההחלטות התקבלו על ידי הקבוצה.
- [ ] בלי תמליל מלא.

---

### T18 – בדיקה סופית לפני הגשה

**ביחד** | **סעיף במטלה:** 8

- [ ] `git clone` נקי, venv חדש, `pip install -e ".[dev]"`.
- [ ] `python -m pytest` – הכול עובר, **לפחות 16 מקרי בדיקה**.
- [ ] בלי אינטרנט: `python -m pytest` ו־`python main.py` עובדים.
- [ ] עם אינטרנט: `python main.py --live` עובד ומסמן LIVE.
- [ ] `git ls-files` לא מכיל `.env` (רק `.env.example`).
- [ ] אין מידע אישי אמיתי ב־`data/`.
- [ ] שלושת commits ה־TDD נראים ב־`git log` של `main`.
- [ ] כל אחד מסוגל להסביר כל מודול, גם כזה שלא כתב.
- [ ] שולחים קישור למאגר.

---

## 3. מיפוי דרישות המטלה למשימות

```text
1    תכנון ההרחבה                                    0.1, T16
2.1  GET, params, timeout, raise_for_status, JSON     T3
2.1  אימות שדות והמרה לאובייקט                       T2
2.1  שימוש עסקי, הפרדה מהתקשורת                       T9, T10
2.2  ארבעה סוגי כשל, Retry 3 עם המתנה, דיווח          T3
2.2  תגובת המערכת לכשל                                T9
2.3  config, .env.example, .gitignore, logging        T1, T3, T8
3    Strategy + Observer, הזרקת תלויות                 T7, T8, T9, T14
4.1  16+ בדיקות, fixture, parametrize, raises, Mock, tmp_path   כל המשימות
4.1  רגרסיה שלב 1                                    T13, T5
4.1  שירות: הצלחה / Timeout / HTTP / שדה חסר, Retry     T3
4.1  async ו-Lock                                     T11, T12
4.1  תהליך משולב                                     T14
4.2  TDD                                              T6
5.1  async: סדרתי מול gather, סדר הקלט                 T11
5.2  Threads, Lock, join, ספירה ומצב סופי              T12
7.1  pyproject, main בלי רשת, --live, סימון המקור      T0, T4, T14
7.2  README                                           T16, T15
7.3  AI_USAGE                                         T17
8    רשימת הגשה                                       T18
```
