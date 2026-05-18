from __future__ import annotations

from typing import Protocol

from PySide6.QtCore import Property, QObject, Signal, Slot

from app.api.errors import QueueApiConnectionError, QueueApiError, QueueApiResponseError
from app.schemas.queue import QueueFormulasResponse


class QueueApiClientProtocol(Protocol):
    def get_formulas(self) -> QueueFormulasResponse:
        ...


class FormulasViewModel(QObject):
    """ViewModel страницы формул модели M/M/1.

    Формулы загружаются с FastAPI-сервера, чтобы desktop-клиент использовал
    тот же API-контракт, что и web-клиент.
    """

    loadingChanged = Signal()
    errorMessageChanged = Signal()
    formulasChanged = Signal()

    def __init__(
        self,
        api_client: QueueApiClientProtocol,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._api_client = api_client

        self._is_loading = False
        self._error_message = ""
        self._model_name = "M/M/1"
        self._description = (
            "Одноканальная система массового обслуживания с пуассоновским "
            "потоком заявок и экспоненциальным временем обслуживания."
        )
        self._stability_condition = "λ < μ"
        self._formulas: dict[str, str] = {
            "utilization": "ρ = λ / μ",
            "average_orders_in_system": "L = λ / (μ - λ)",
            "average_waiting_time": "Wq = λ / (μ × (μ - λ))",
            "average_time_in_system": "W = 1 / (μ - λ)",
        }

    @Property(bool, notify=loadingChanged)
    def isLoading(self) -> bool:
        return self._is_loading

    @Property(str, notify=errorMessageChanged)
    def errorMessage(self) -> str:
        return self._error_message

    @Property(str, notify=formulasChanged)
    def modelName(self) -> str:
        return self._model_name

    @Property(str, notify=formulasChanged)
    def description(self) -> str:
        return self._description

    @Property(str, notify=formulasChanged)
    def stabilityCondition(self) -> str:
        return self._stability_condition

    @Property("QVariantList", notify=formulasChanged)
    def formulaItems(self) -> list[dict[str, str]]:
        labels = {
            "utilization": "Коэффициент загрузки",
            "average_orders_in_system": "Среднее число заказов в системе",
            "average_waiting_time": "Среднее время ожидания начала обработки",
            "average_time_in_system": "Среднее время пребывания заказа в системе",
        }

        hints = {
            "utilization": "Показывает долю времени, в течение которого клерк занят.",
            "average_orders_in_system": "Учитывает и очередь, и заказ в обслуживании.",
            "average_waiting_time": "Время до начала обработки заказа.",
            "average_time_in_system": "Ожидание плюс время обработки заказа.",
        }

        preferred_order = [
            "utilization",
            "average_orders_in_system",
            "average_waiting_time",
            "average_time_in_system",
        ]

        ordered_keys = [
            key for key in preferred_order if key in self._formulas
        ] + [
            key for key in self._formulas if key not in preferred_order
        ]

        return [
            {
                "key": key,
                "title": labels.get(key, key),
                "formula": self._formulas[key],
                "hint": hints.get(key, ""),
            }
            for key in ordered_keys
        ]

    @Slot()
    def loadFormulas(self) -> None:
        self._set_loading(True)
        self._clear_error()

        try:
            response = self._api_client.get_formulas()

            self._model_name = response.model_name
            self._description = response.description
            self._stability_condition = response.stability_condition
            self._formulas = dict(response.formulas)

            self.formulasChanged.emit()
        except QueueApiConnectionError:
            self._set_error(
                "Не удалось подключиться к FastAPI-серверу. "
                "Проверьте, что сервер запущен."
            )
        except QueueApiResponseError as exc:
            self._set_error(f"Сервер вернул ошибку: {exc}")
        except QueueApiError as exc:
            self._set_error(f"Ошибка API-клиента: {exc}")
        except Exception as exc:
            self._set_error(f"Не удалось загрузить формулы: {exc}")
        finally:
            self._set_loading(False)

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
