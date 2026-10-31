def classify_heat_level(apparent_temperature_c):
    if apparent_temperature_c >= 39:
        return "danger"
    if apparent_temperature_c >= 32:
        return "caution"
    return "normal"