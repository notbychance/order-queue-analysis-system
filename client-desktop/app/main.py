from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from app.api.queue_api_client import create_queue_api_client
from app.core.settings import get_settings
from app.services.history_service import create_history_service
from app.viewmodels.analysis_view_model import AnalysisViewModel
from app.viewmodels.formulas_view_model import FormulasViewModel
from app.viewmodels.history_view_model import HistoryViewModel
from app.viewmodels.theme_view_model import ThemeViewModel


def _resource_path(*parts: str) -> Path:
    """Вернуть путь к ресурсам в dev-режиме и внутри PyInstaller-сборки."""

    if getattr(sys, "frozen", False):
        base_dir = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
        return base_dir.joinpath(*parts)

    return Path(__file__).resolve().parent.joinpath(*parts)


QML_DIR = _resource_path("ui", "qml")
MAIN_QML = QML_DIR / "Main.qml"


def main() -> int:
    settings = get_settings()

    app = QGuiApplication(sys.argv)
    app.setApplicationName(settings.app_name)
    app.setOrganizationName("Coursework")
    app.setOrganizationDomain("local")

    # Сервер FastAPI историю не хранит.
    # История desktop-клиента хранится локально в SQLite.
    history_service = create_history_service(settings)
    history_service.initialize()

    queue_api_client = create_queue_api_client(settings)

    analysis_view_model = AnalysisViewModel(
        api_client=queue_api_client,
        history_service=history_service,
    )
    history_view_model = HistoryViewModel(
        history_service=history_service,
    )
    formulas_view_model = FormulasViewModel(
        api_client=queue_api_client,
    )
    theme_view_model = ThemeViewModel(
        default_mode=settings.theme,
    )

    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("appName", settings.app_name)
    engine.rootContext().setContextProperty("analysisViewModel", analysis_view_model)
    engine.rootContext().setContextProperty("historyViewModel", history_view_model)
    engine.rootContext().setContextProperty("formulasViewModel", formulas_view_model)
    engine.rootContext().setContextProperty("themeViewModel", theme_view_model)

    engine.load(QUrl.fromLocalFile(str(MAIN_QML)))

    if not engine.rootObjects():
        queue_api_client.close()
        return 1

    exit_code = app.exec()
    queue_api_client.close()

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
