from __future__ import annotations

from datetime import datetime
from typing import Protocol

from PySide6.QtCore import Property, QObject, Signal, Slot

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


class HistoryViewModel(QObject):
    """ViewModel страницы локальной истории расчетов.

    QML работает только с этой ViewModel.
    SQLAlchemy и репозиторий остаются внутри сервисного слоя.
    """

    loadingChanged = Signal()
    errorMessageChanged = Signal()
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
        self._history_items: list[HistoryItem] = []

    @Property(bool, notify=loadingChanged)
    def isLoading(self) -> bool:
        return self._is_loading

    @Property(str, notify=errorMessageChanged)
    def errorMessage(self) -> str:
        return self._error_message

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
    def deleteHistoryItem(self, record_id: str) -> None:
        self._clear_error()

        if not record_id:
            self._set_error("Не удалось удалить запись: пустой идентификатор.")
            return

        try:
            deleted = self._history_service.delete_history_item(record_id)

            if not deleted:
                self._set_error("Запись истории не найдена.")
                return

            self.loadHistory()
        except Exception as exc:
            self._set_error(f"Не удалось удалить запись истории: {exc}")

    @Slot()
    def clearHistory(self) -> None:
        self._clear_error()

        try:
            self._history_service.clear_history()
            self.loadHistory()
        except Exception as exc:
            self._set_error(f"Не удалось очистить историю: {exc}")

    @Slot(str)
    def repeatHistoryItem(self, record_id: str) -> None:
        self._clear_error()

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
