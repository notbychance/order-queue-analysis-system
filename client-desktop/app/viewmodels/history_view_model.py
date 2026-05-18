from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Protocol

from PySide6.QtCore import Property, QObject, QUrl, Signal, Slot

from app.schemas.history import HistoryItem


class HistoryServiceProtocol(Protocol):
    def get_history(self, limit: int | None = None) -> list[HistoryItem]:
        ...

    def get_history_item(self, record_id: str) -> HistoryItem | None:
        ...

    def delete_history_item(self, record_id: str) -> bool:
        ...

    def clear_history(self) -> int:
        ...

    def count_history_items(self) -> int:
        ...

    def export_history_to_file(self, file_path: str | Path) -> Path:
        ...

    def import_history_from_file(
        self,
        file_path: str | Path,
        *,
        replace: bool = False,
    ) -> int:
        ...


class HistoryViewModel(QObject):
    """ViewModel страницы локальной истории расчетов.

    QML работает только с этой ViewModel.
    SQLAlchemy и репозиторий остаются внутри сервисного слоя.
    """

    loadingChanged = Signal()
    errorMessageChanged = Signal()
    statusMessageChanged = Signal()
    historyChanged = Signal()
    repeatRequested = Signal(str, str)

    def __init__(
        self,
        history_service: HistoryServiceProtocol,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._history_service = history_service

        self._is_loading = False
        self._error_message = ""
        self._status_message = ""
        self._history_items: list[HistoryItem] = []

    @Property(bool, notify=loadingChanged)
    def isLoading(self) -> bool:
        return self._is_loading

    @Property(str, notify=errorMessageChanged)
    def errorMessage(self) -> str:
        return self._error_message

    @Property(str, notify=statusMessageChanged)
    def statusMessage(self) -> str:
        return self._status_message

    @Property("QVariantList", notify=historyChanged)
    def historyItems(self) -> list[dict[str, object]]:
        return [self._to_qml_item(item) for item in self._history_items]

    @Property(bool, notify=historyChanged)
    def hasHistory(self) -> bool:
        return len(self._history_items) > 0

    @Property(int, notify=historyChanged)
    def historyCount(self) -> int:
        return len(self._history_items)

    @Slot()
    def loadHistory(self) -> None:
        self._set_loading(True)
        self._clear_error()

        try:
            self._history_items = self._history_service.get_history()
            self.historyChanged.emit()
        except Exception as exc:
            self._set_error(f"Не удалось загрузить историю: {exc}")
        finally:
            self._set_loading(False)

    @Slot(str)
    def exportHistory(self, file_url: str) -> None:
        self._clear_error()
        self._clear_status()

        try:
            file_path = self._path_from_qml_url(file_url)
            exported_path = self._history_service.export_history_to_file(file_path)
            self._set_status(f"История экспортирована: {exported_path}")
        except Exception as exc:
            self._set_error(f"Не удалось экспортировать историю: {exc}")

    @Slot(str)
    def importHistory(self, file_url: str) -> None:
        self._clear_error()
        self._clear_status()

        try:
            file_path = self._path_from_qml_url(file_url)
            imported_count = self._history_service.import_history_from_file(
                file_path,
                replace=False,
            )

            self.loadHistory()
            self._set_status(f"Импортировано записей: {imported_count}")
        except Exception as exc:
            self._set_error(f"Не удалось импортировать историю: {exc}")

    @Slot(str)
    def deleteHistoryItem(self, record_id: str) -> None:
        self._clear_error()
        self._clear_status()

        if not record_id:
            self._set_error("Не удалось удалить запись: пустой идентификатор.")
            return

        try:
            deleted = self._history_service.delete_history_item(record_id)

            if not deleted:
                self._set_error("Запись истории не найдена.")
                return

            self.loadHistory()
            self._set_status("Запись истории удалена.")
        except Exception as exc:
            self._set_error(f"Не удалось удалить запись истории: {exc}")

    @Slot()
    def clearHistory(self) -> None:
        self._clear_error()
        self._clear_status()

        try:
            deleted_count = self._history_service.clear_history()
            self.loadHistory()
            self._set_status(f"История очищена. Удалено записей: {deleted_count}")
        except Exception as exc:
            self._set_error(f"Не удалось очистить историю: {exc}")

    @Slot(str)
    def repeatHistoryItem(self, record_id: str) -> None:
        self._clear_error()
        self._clear_status()

        if not record_id:
            self._set_error("Не удалось повторить расчет: пустой идентификатор.")
            return

        try:
            item = self._history_service.get_history_item(record_id)
        except Exception as exc:
            self._set_error(f"Не удалось получить запись истории: {exc}")
            return

        if item is None:
            self._set_error("Запись истории не найдена.")
            return

        self.repeatRequested.emit(
            self._format_number(item.lambda_rate),
            self._format_number(item.mu_rate),
        )

    def _set_loading(self, value: bool) -> None:
        if self._is_loading == value:
            return

        self._is_loading = value
        self.loadingChanged.emit()

    def _set_error(self, message: str) -> None:
        if self._error_message == message:
            return

        self._error_message = message
        self.errorMessageChanged.emit()

    def _clear_error(self) -> None:
        self._set_error("")

    def _set_status(self, message: str) -> None:
        if self._status_message == message:
            return

        self._status_message = message
        self.statusMessageChanged.emit()

    def _clear_status(self) -> None:
        self._set_status("")

    @classmethod
    def _to_qml_item(cls, item: HistoryItem) -> dict[str, object]:
        return {
            "id": item.id,
            "createdAt": cls._format_datetime(item.created_at),
            "lambdaRate": cls._format_number(item.lambda_rate),
            "muRate": cls._format_number(item.mu_rate),
            "isStable": item.is_stable,
            "stabilityText": "Устойчива" if item.is_stable else "Неустойчива",
            "utilizationPercent": f"{cls._format_number(item.utilization_percent)} %",
            "averageOrders": cls._format_nullable_number(item.average_orders_in_system),
            "averageWaitingTimeHours": cls._format_nullable_hours(
                item.average_waiting_time_hours
            ),
            "averageTimeInSystemHours": cls._format_nullable_hours(
                item.average_time_in_system_hours
            ),
            "conclusion": item.conclusion,
        }

    @staticmethod
    def _path_from_qml_url(file_url: str) -> Path:
        url = QUrl(file_url)

        if url.isLocalFile():
            return Path(url.toLocalFile())

        return Path(file_url).expanduser()

    @staticmethod
    def _format_datetime(value: datetime) -> str:
        return value.strftime("%d.%m.%Y %H:%M")

    @staticmethod
    def _format_nullable_number(value: float | None) -> str:
        if value is None:
            return "—"

        return HistoryViewModel._format_number(value)

    @staticmethod
    def _format_nullable_hours(value: float | None) -> str:
        if value is None:
            return "—"

        return f"{HistoryViewModel._format_number(value)} ч"

    @staticmethod
    def _format_number(value: float) -> str:
        rounded = round(value, 4)

        if rounded.is_integer():
            return str(int(rounded))

        return f"{rounded:.4f}".rstrip("0").rstrip(".")
