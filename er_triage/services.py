import logging
from dataclasses import dataclass

from .api_client import WeatherServiceError
from .models import WeatherSnapshot
from .observers import PatientFlaggedEvent

logger = logging.getLogger(__name__)

HEAT_LEVELS = ("normal", "caution", "danger")

# Thresholds follow the heat index categories of the US National Weather Service
# (Extreme Caution from 90°F, Danger from 103°F), rounded to whole °C.
# Open-Meteo's apparent temperature uses a different formula, so this is an approximation.
CAUTION_THRESHOLD_C = 32
DANGER_THRESHOLD_C = 39


def classify_heat_level(apparent_temperature_c):
    """Return "normal", "caution" or "danger" for an apparent temperature in °C."""
    if apparent_temperature_c >= DANGER_THRESHOLD_C:
        return "danger"
    if apparent_temperature_c >= CAUTION_THRESHOLD_C:
        return "caution"
    return "normal"


@dataclass
class HeatCheckResult:
    status: str
    heat_level: str | None
    snapshot: WeatherSnapshot | None
    flagged_patient_ids: list[str]
    error_message: str | None


class HeatAlertService:
    def __init__(self, weather_client, publisher, strategies):
        missing_levels = set(HEAT_LEVELS) - strategies.keys()
        if missing_levels:
            raise ValueError(f"Missing flagging strategy for heat levels: {sorted(missing_levels)}")
        self.weather_client = weather_client
        self.publisher = publisher
        self.strategies = strategies

    def run_check(self, patients):
        try:
            snapshot = self.weather_client.get_weather()
        except WeatherServiceError as error:
            # Without valid weather data nobody is flagged; the clinical urgency stays as it is
            logger.warning("Heat check skipped, weather data unavailable: %s", error)
            return HeatCheckResult("unavailable", None, None, [], str(error))

        heat_level = classify_heat_level(snapshot.apparent_temperature_c)
        selected = self.strategies[heat_level].select(patients)

        for patient in selected:
            patient.flag_for_reassessment(f"heat:{heat_level}")
            self.publisher.publish(PatientFlaggedEvent(patient, heat_level))

        flagged_ids = [patient.patient_id for patient in selected]
        logger.info("Heat level %s from %s data: %d patients flagged",
                    heat_level, snapshot.source, len(flagged_ids))
        return HeatCheckResult("applied", heat_level, snapshot, flagged_ids, None)