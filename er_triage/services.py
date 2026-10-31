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