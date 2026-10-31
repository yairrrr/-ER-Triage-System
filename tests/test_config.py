import pytest

from er_triage.config import read_float, read_int, read_str


def test_read_str_uses_default_when_variable_is_missing(monkeypatch):
    monkeypatch.delenv("TEST_CONFIG_VALUE", raising=False)
    assert read_str("TEST_CONFIG_VALUE", "INFO") == "INFO"


def test_read_int_reads_value_from_environment(monkeypatch):
    monkeypatch.setenv("TEST_CONFIG_VALUE", "7")
    assert read_int("TEST_CONFIG_VALUE", 3) == 7


def test_read_float_reads_value_from_environment(monkeypatch):
    monkeypatch.setenv("TEST_CONFIG_VALUE", "32.5")
    assert read_float("TEST_CONFIG_VALUE", 0.0) == 32.5


@pytest.mark.parametrize("reader, bad_value", [
    (read_int, "abc"),
    (read_int, "2.5"),
    (read_float, "north"),
])
def test_invalid_value_raises_value_error_with_variable_name(monkeypatch, reader, bad_value):
    monkeypatch.setenv("TEST_CONFIG_VALUE", bad_value)
    with pytest.raises(ValueError, match="TEST_CONFIG_VALUE"):
        reader("TEST_CONFIG_VALUE", 0)