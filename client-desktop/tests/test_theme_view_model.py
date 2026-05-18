from __future__ import annotations

import pytest
from PySide6.QtCore import QSettings

from app.viewmodels.theme_view_model import ThemeViewModel


def make_qsettings(tmp_path) -> QSettings:
    settings_path = tmp_path / "settings.ini"
    settings = QSettings(str(settings_path), QSettings.Format.IniFormat)
    settings.clear()
    settings.sync()
    return settings


@pytest.mark.unit
@pytest.mark.ui
def test_theme_view_model_uses_default_mode(tmp_path):
    qsettings = make_qsettings(tmp_path)

    view_model = ThemeViewModel(default_mode="dark", qsettings=qsettings)

    assert view_model.themeMode == "dark"
    assert view_model.isDark is True
    assert view_model.themeTitle == "Темная"
    assert view_model.themeIndex == 1


@pytest.mark.unit
@pytest.mark.ui
def test_theme_view_model_falls_back_to_system_for_invalid_default(tmp_path):
    qsettings = make_qsettings(tmp_path)

    view_model = ThemeViewModel(default_mode="invalid", qsettings=qsettings)

    assert view_model.themeMode == "system"
    assert view_model.themeTitle == "Как в системе"


@pytest.mark.unit
@pytest.mark.ui
def test_set_theme_mode_updates_and_persists_value(tmp_path):
    qsettings = make_qsettings(tmp_path)
    view_model = ThemeViewModel(default_mode="light", qsettings=qsettings)

    view_model.setThemeMode("dark")

    assert view_model.themeMode == "dark"
    assert view_model.isDark is True
    assert qsettings.value("ui/theme_mode") == "dark"


@pytest.mark.unit
@pytest.mark.ui
def test_saved_theme_has_priority_over_default_mode(tmp_path):
    qsettings = make_qsettings(tmp_path)
    qsettings.setValue("ui/theme_mode", "dark")
    qsettings.sync()

    view_model = ThemeViewModel(default_mode="light", qsettings=qsettings)

    assert view_model.themeMode == "dark"


@pytest.mark.unit
@pytest.mark.ui
def test_toggle_theme_switches_between_light_and_dark(tmp_path):
    qsettings = make_qsettings(tmp_path)
    view_model = ThemeViewModel(default_mode="light", qsettings=qsettings)

    view_model.toggleTheme()

    assert view_model.themeMode == "dark"
    assert view_model.themeButtonText == "Светлая тема"

    view_model.toggleTheme()

    assert view_model.themeMode == "light"
    assert view_model.themeButtonText == "Темная тема"


@pytest.mark.unit
@pytest.mark.ui
def test_set_system_theme(tmp_path):
    qsettings = make_qsettings(tmp_path)
    view_model = ThemeViewModel(default_mode="light", qsettings=qsettings)

    view_model.setSystemTheme()

    assert view_model.themeMode == "system"
    assert view_model.themeTitle == "Как в системе"


@pytest.mark.unit
@pytest.mark.ui
def test_theme_options_are_available_for_qml_combobox(tmp_path):
    qsettings = make_qsettings(tmp_path)
    view_model = ThemeViewModel(default_mode="light", qsettings=qsettings)

    options = view_model.themeOptions

    assert options == [
        {"value": "light", "title": "Светлая"},
        {"value": "dark", "title": "Темная"},
        {"value": "system", "title": "Как в системе"},
    ]
