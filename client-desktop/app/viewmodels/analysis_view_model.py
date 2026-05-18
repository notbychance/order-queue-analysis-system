from __future__ import annotations

from typing import Protocol

from PySide6.QtCore import Property, QObject, QThread, Signal, Slot

from app.api.errors import QueueApiConnectionError, QueueApiError, QueueApiResponseError
from app.schemas.history import HistoryCreate, HistoryItem
from app.schemas.queue import QueueAnalysisRequest, QueueAnalysisResponse


class QueueApiClientProtocol(Protocol):
    def analyze_queue(self, request: QueueAnalysisRequest) -> QueueAnalysisResponse:
        ...


class HistoryServiceProtocol(Protocol):
    def add_history_item(self, data: HistoryCreate) -> HistoryItem:
        ...


class AnalysisWorker(QObject):
    """Worker для выполнения HTTP-запроса и сохранения истории вне UI-потока."""

    succeeded = Signal(object)
    failed = Signal(str)

    def __init__(
        self,
        api_client: QueueApiClientProtocol,
        history_service: HistoryServiceProtocol,
        request: QueueAnalysisRequest,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._api_client = api_client
        self._history_service = history_service
        self._request = request

    @Slot()
    def run(self) -> None:
        try:
            result = self._api_client.analyze_queue(self._request)

            self._history_service.add_history_item(
                AnalysisViewModel.history_create_from_response(result)
            )

            self.succeeded.emit(result)
        except QueueApiConnectionError:
            self.failed.emit(
                "Не удалось подключиться к FastAPI-серверу. "
                "Проверьте, что сервер запущен."
            )
        except QueueApiResponseError as exc:
            self.failed.emit(f"Сервер вернул ошибку: {exc}")
        except QueueApiError as exc:
            self.failed.emit(f"Ошибка API-клиента: {exc}")
        except Exception as exc:
            self.failed.emit(f"Не удалось выполнить анализ: {exc}")


class AnalysisViewModel(QObject):
    """ViewModel страницы анализа для QML.

    QML не обращается напрямую ни к FastAPI, ни к SQLAlchemy.
    Он вызывает методы этой ViewModel, а она:
    1. валидирует введенные параметры;
    2. запускает анализ в отдельном QThread;
    3. получает результат анализа;
    4. отдает QML готовые свойства для отображения.

    HTTP-запрос к FastAPI и сохранение истории выполняются не в UI-потоке,
    поэтому окно приложения не зависает на время запроса.
    """

    loadingChanged = Signal()
    errorMessageChanged = Signal()
    resultChanged = Signal()

    def __init__(
        self,
        api_client: QueueApiClientProtocol,
        history_service: HistoryServiceProtocol,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._api_client = api_client
        self._history_service = history_service

        self._is_loading = False
        self._error_message = ""
        self._result: QueueAnalysisResponse | None = None

        self._worker_thread: QThread | None = None
        self._worker: AnalysisWorker | None = None

    @Property(bool, notify=loadingChanged)
    def isLoading(self) -> bool:
        return self._is_loading

    @Property(str, notify=errorMessageChanged)
    def errorMessage(self) -> str:
        return self._error_message

    @Property(bool, notify=resultChanged)
    def hasResult(self) -> bool:
        return self._result is not None

    @Property(bool, notify=resultChanged)
    def resultIsStable(self) -> bool:
        return bool(self._result and self._result.is_stable)

    @Property(float, notify=resultChanged)
    def lambdaRate(self) -> float:
        return self._result.lambda_rate if self._result else 0.0

    @Property(float, notify=resultChanged)
    def muRate(self) -> float:
        return self._result.mu_rate if self._result else 0.0

    @Property(str, notify=resultChanged)
    def lambdaRateText(self) -> str:
        if self._result is None:
            return "—"

        return self._format_number(self._result.lambda_rate)

    @Property(str, notify=resultChanged)
    def muRateText(self) -> str:
        if self._result is None:
            return "—"

        return self._format_number(self._result.mu_rate)

    @Property(str, notify=resultChanged)
    def stabilityText(self) -> str:
        if self._result is None:
            return "—"

        return "Устойчива" if self._result.is_stable else "Неустойчива"

    @Property(str, notify=resultChanged)
    def utilizationPercentText(self) -> str:
        if self._result is None:
            return "—"

        return f"{self._format_number(self._result.utilization_percent)} %"

    @Property(str, notify=resultChanged)
    def averageOrdersText(self) -> str:
        if self._result is None or self._result.average_orders_in_system is None:
            return "—"

        return self._format_number(self._result.average_orders_in_system)

    @Property(str, notify=resultChanged)
    def averageWaitingTimeText(self) -> str:
        if self._result is None or self._result.average_waiting_time_hours is None:
            return "—"

        return f"{self._format_number(self._result.average_waiting_time_hours)} ч"

    @Property(str, notify=resultChanged)
    def averageTimeInSystemText(self) -> str:
        if self._result is None or self._result.average_time_in_system_hours is None:
            return "—"

        return f"{self._format_number(self._result.average_time_in_system_hours)} ч"

    @Property(str, notify=resultChanged)
    def conclusionText(self) -> str:
        if self._result is None:
            return "После расчета здесь появится заключение по системе."

        return self._result.conclusion

    @Slot(str, str)
    def analyze(self, lambda_rate_text: str, mu_rate_text: str) -> None:
        if self._is_loading:
            return

        self._clear_error()

        try:
            request = QueueAnalysisRequest(
                lambda_rate=self._parse_rate(lambda_rate_text, "λ"),
                mu_rate=self._parse_rate(mu_rate_text, "μ"),
            )
        except ValueError as exc:
            self._set_error(str(exc))
            return

        self._start_worker(request)

    @Slot()
    def clearResult(self) -> None:
        if self._is_loading:
            return

        self._clear_error()
        self._result = None
        self.resultChanged.emit()

    def _start_worker(self, request: QueueAnalysisRequest) -> None:
        self._set_loading(True)

        thread = QThread(self)
        worker = AnalysisWorker(
            api_client=self._api_client,
            history_service=self._history_service,
            request=request,
        )

        worker.moveToThread(thread)

        thread.started.connect(worker.run)

        worker.succeeded.connect(self._handle_worker_success)
        worker.failed.connect(self._handle_worker_failure)

        worker.succeeded.connect(thread.quit)
        worker.failed.connect(thread.quit)

        worker.succeeded.connect(worker.deleteLater)
        worker.failed.connect(worker.deleteLater)

        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._handle_worker_finished)

        self._worker_thread = thread
        self._worker = worker

        thread.start()

    @Slot(object)
    def _handle_worker_success(self, result: object) -> None:
        if not isinstance(result, QueueAnalysisResponse):
            self._set_error("Сервер вернул результат в неизвестном формате.")
            return

        self._result = result
        self.resultChanged.emit()

    @Slot(str)
    def _handle_worker_failure(self, message: str) -> None:
        self._set_error(message)

    @Slot()
    def _handle_worker_finished(self) -> None:
        self._worker_thread = None
        self._worker = None
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

    @staticmethod
    def _parse_rate(value: str, field_name: str) -> float:
        normalized = value.strip().replace(",", ".")

        if not normalized:
            raise ValueError(f"Введите значение {field_name}.")

        try:
            parsed = float(normalized)
        except ValueError as exc:
            raise ValueError(f"Значение {field_name} должно быть числом.") from exc

        if field_name == "λ" and parsed < 0:
            raise ValueError("Интенсивность поступления λ не может быть отрицательной.")

        if field_name == "μ" and parsed <= 0:
            raise ValueError("Интенсивность обслуживания μ должна быть больше нуля.")

        return parsed

    @staticmethod
    def history_create_from_response(
        response: QueueAnalysisResponse,
    ) -> HistoryCreate:
        return HistoryCreate(
            lambda_rate=response.lambda_rate,
            mu_rate=response.mu_rate,
            is_stable=response.is_stable,
            utilization=response.utilization,
            utilization_percent=response.utilization_percent,
            average_orders_in_system=response.average_orders_in_system,
            average_waiting_time=response.average_waiting_time,
            average_waiting_time_hours=response.average_waiting_time_hours,
            average_time_in_system=response.average_time_in_system,
            average_time_in_system_hours=response.average_time_in_system_hours,
            conclusion=response.conclusion,
        )

    @staticmethod
    def _format_number(value: float) -> str:
        rounded = round(value, 4)

        if rounded.is_integer():
            return str(int(rounded))

        return f"{rounded:.4f}".rstrip("0").rstrip(".")
