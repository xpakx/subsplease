from pathlib import Path
from pytest import MonkeyPatch
from subsplease.config import (
        get_config_location,
        get_cache_location,
        get_data_location
)


def test_get_config_location_custom_env(monkeypatch: MonkeyPatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", "/tmp/custom_config")
    result = get_config_location()
    assert result == Path("/tmp/custom_config/subsplease")


def test_get_config_location_default(monkeypatch: MonkeyPatch):
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    monkeypatch.setenv("HOME", "/home/user")
    result = get_config_location()
    assert result == Path("/home/user/.config/subsplease")


def test_get_cache_location_default(monkeypatch: MonkeyPatch):
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
    monkeypatch.setenv("HOME", "/home/user")
    result = get_cache_location()
    assert result == Path("/home/user/.cache/subsplease")


def test_get_data_location_default(monkeypatch: MonkeyPatch):
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
    monkeypatch.setenv("HOME", "/home/user")
    result = get_data_location()
    assert result == Path("/home/user/.local/share/subsplease")


def test_empty_home_fallback(monkeypatch: MonkeyPatch):
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    monkeypatch.setenv("HOME", "")
    result = get_config_location()
    assert result == Path(".config/subsplease")
