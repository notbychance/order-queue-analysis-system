from __future__ import annotations

from PySide6.QtCore import Property, QObject, QSettings, Qt, Signal, Slot
from PySide6.QtGui import QGuiApplication


ThemeMode = str

LIGHT_THEME: ThemeMode = "light"
DARK_THEME: ThemeMode = "dark"
SYSTEM_THEME: ThemeMode = "system"

THEME_MODES: tuple[ThemeMode, ...] = (
    LIGHT_THEME,
    DARK_THEME,
    SYSTEM_THEME,
)


class ThemeViewModel(QObject):
    """ViewModel темы desktop-приложения.

    Тема сохраняется через QSettings, поэтому выбор пользователя переживает
    перезапуск приложения. Значение THEME из .env используется только как
    первоначальное значение, если пользователь еще ничего не выбирал.
    """

    themeChanged = Signal()

    SETTINGS_KEY = "ui/theme_mode"

    def __init__(
        self,
        default_mode: ThemeMode = SYSTEM_THEME,
        qsettings: QSettings | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._settings = qsettings or QSettings()
        self._mode = self._load_mode(default_mode)

    @Property(str, notify=themeChanged)
    def themeMode(self) -> str:
        return self._mode

    @Property(bool, notify=themeChanged)
    def isDark(self) -> bool:
        if self._mode == DARK_THEME:
            return True

        if self._mode == LIGHT_THEME:
            return False

        return self._system_prefers_dark()

    @Property(int, notify=themeChanged)
    def themeIndex(self) -> int:
        try:
            return list(THEME_MODES).index(self._mode)
        except ValueError:
            return list(THEME_MODES).index(SYSTEM_THEME)

    @Property(str, notify=themeChanged)
    def themeTitle(self) -> str:
        return self._title_for_mode(self._mode)

    @Property(str, notify=themeChanged)
    def themeButtonText(self) -> str:
        return "Светлая тема" if self.isDark else "Темная тема"

    @Property("QVariantList", notify=themeChanged)
    def themeOptions(self) -> list[dict[str, str]]:
        return [
            {
                "value": LIGHT_THEME,
                "title": "Светлая",
            },
            {
                "value": DARK_THEME,
                "title": "Темная",
            },
            {
                "value": SYSTEM_THEME,
                "title": "Как в системе",
            },
        ]

    @Slot(str)
    def setThemeMode(self, mode: str) -> None:
        normalized_mode = self._normalize_mode(mode, fallback=self._mode)

        if normalized_mode == self._mode:
            return

        self._mode = normalized_mode
        self._save_mode(normalized_mode)
        self.themeChanged.emit()

    @Slot()
    def setLightTheme(self) -> None:
        self.setThemeMode(LIGHT_THEME)

    @Slot()
    def setDarkTheme(self) -> None:
        self.setThemeMode(DARK_THEME)

    @Slot()
    def setSystemTheme(self) -> None:
        self.setThemeMode(SYSTEM_THEME)

    @Slot()
    def toggleTheme(self) -> None:
        self.setThemeMode(LIGHT_THEME if self.isDark else DARK_THEME)

    def _load_mode(self, default_mode: str) -> ThemeMode:
        fallback = self._normalize_mode(default_mode, fallback=SYSTEM_THEME)
        stored_mode = self._settings.value(self.SETTINGS_KEY, fallback)

        if isinstance(stored_mode, str):
            return self._normalize_mode(stored_mode, fallback=fallback)

        return fallback

    def _save_mode(self, mode: ThemeMode) -> None:
        self._settings.setValue(self.SETTINGS_KEY, mode)
        self._settings.sync()

    @staticmethod
    def _normalize_mode(mode: str, *, fallback: ThemeMode) -> ThemeMode:
        normalized_mode = mode.strip().lower()

        if normalized_mode in THEME_MODES:
            return normalized_mode

        return fallback

    @staticmethod
    def _title_for_mode(mode: ThemeMode) -> str:
        if mode == LIGHT_THEME:
            return "Светлая"

        if mode == DARK_THEME:
            return "Темная"

        return "Как в системе"

    @staticmethod
    def _system_prefers_dark() -> bool:
        app = QGuiApplication.instance()

        if app is None:
            return False

        color_scheme = app.styleHints().colorScheme()

        return color_scheme == Qt.ColorScheme.Dark
