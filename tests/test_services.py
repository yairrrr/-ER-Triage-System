import pytest

from er_triage.services import classify_heat_level


@pytest.mark.parametrize("apparent_temperature, expected_level", [
    (20, "normal"),
    (31.9, "normal"),
    (32, "caution"),
    (38.9, "caution"),
    (39, "danger"),
    (45, "danger"),
])
def test_classify_heat_level(apparent_temperature, expected_level):
    assert classify_heat_level(apparent_temperature) == expected_level