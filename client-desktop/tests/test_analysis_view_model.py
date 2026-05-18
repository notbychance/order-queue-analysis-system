from __future__ import annotations

import pytest

from app.api.errors import QueueApiConnectionError
from app.schemas.history import HistoryCreate
from app.schemas.queue import QueueAnalysisRequest, QueueAnalysisResponse
from app.viewmodels.analysis_view_model import AnalysisViewModel


def make_response(
    *,
    is_stable: bool = True,
) -> QueueAnalysisResponse:
    return QueueAnalysisResponse(
        lambda_rate=6.0,
        mu_rate=8.0,
        arrival_rate_unit="заказов/день",
        service_rate_unit="заказов/день",
        time_unit="дней",
        is_stable=is_stable,
        utilization=0.75,
        utilization_percent=75.0,
        average_orders_in_system=3.0 if is_stable else None,
        average_waiting_time=0.375 if is_stable else None,
        average_waiting_time_hours=9.0 if is_stable else None,
        average_time_in_system=0.5 if is_stable else None,
        average_time_in_system_hours=12.0 if is_stable else None,
        conclusion="Система устойчива." if is_stable else "Система неустойчива.",
    )


class FakeApiClient:
    def __init__(self, response: QueueAnalysisResponse | None = None) -> None:
        self.response = response or make_response()
        self.requests: list[QueueAnalysisRequest] = []
        self.raise_connection_error = False

    def analyze_queue(self, request: QueueAnalysisRequest) -> QueueAnalysisResponse:
        self.requests.append(request)

        if self.raise_connection_error:
            raise QueueApiConnectionError("connection failed")

        return self.response


class FakeHistoryService:
    def __init__(self) -> None:
        self.items: list[HistoryCreate] = []

    def add_history_item(self, data: HistoryCreate):
        self.items.append(data)
        return object()


@pytest.mark.unit
@pytest.mark.ui
def test_analyze_calls_api_and_saves_history():
    api_client = FakeApiClient()
    history_service = FakeHistoryService()
    view_model = AnalysisViewModel(api_client, history_service)

    view_model.analyze("6", "8")

    assert view_model.hasResult is True
    assert view_model.errorMessage == ""
    assert view_model.utilizationPercentText == "75 %"
    assert view_model.averageOrdersText == "3"
    assert view_model.averageWaitingTimeText == "9 ч"
    assert view_model.averageTimeInSystemText == "12 ч"

    assert len(api_client.requests) == 1
    assert api_client.requests[0].lambda_rate == 6.0
    assert api_client.requests[0].mu_rate == 8.0

    assert len(history_service.items) == 1
    assert history_service.items[0].lambda_rate == 6.0
    assert history_service.items[0].mu_rate == 8.0
    assert history_service.items[0].conclusion == "Система устойчива."


@pytest.mark.unit
@pytest.mark.ui
def test_analyze_accepts_comma_decimal_separator():
    api_client = FakeApiClient()
    history_service = FakeHistoryService()
    view_model = AnalysisViewModel(api_client, history_service)

    view_model.analyze("6,5", "8,5")

    assert api_client.requests[0].lambda_rate == 6.5
    assert api_client.requests[0].mu_rate == 8.5


@pytest.mark.unit
@pytest.mark.ui
def test_analyze_sets_error_for_empty_lambda():
    api_client = FakeApiClient()
    history_service = FakeHistoryService()
    view_model = AnalysisViewModel(api_client, history_service)

    view_model.analyze("", "8")

    assert "Введите значение λ" in view_model.errorMessage
    assert view_model.hasResult is False
    assert api_client.requests == []
    assert history_service.items == []


@pytest.mark.unit
@pytest.mark.ui
def test_analyze_sets_error_for_invalid_mu():
    api_client = FakeApiClient()
    history_service = FakeHistoryService()
    view_model = AnalysisViewModel(api_client, history_service)

    view_model.analyze("6", "abc")

    assert "μ должно быть числом" in view_model.errorMessage
    assert view_model.hasResult is False


@pytest.mark.unit
@pytest.mark.ui
def test_analyze_handles_connection_error():
    api_client = FakeApiClient()
    api_client.raise_connection_error = True
    history_service = FakeHistoryService()
    view_model = AnalysisViewModel(api_client, history_service)

    view_model.analyze("6", "8")

    assert "Не удалось подключиться" in view_model.errorMessage
    assert view_model.hasResult is False
    assert history_service.items == []


@pytest.mark.unit
@pytest.mark.ui
def test_clear_result_resets_result_and_error():
    api_client = FakeApiClient()
    history_service = FakeHistoryService()
    view_model = AnalysisViewModel(api_client, history_service)

    view_model.analyze("6", "8")
    view_model.clearResult()

    assert view_model.hasResult is False
    assert view_model.conclusionText == "После расчета здесь появится заключение по системе."
    assert view_model.errorMessage == ""
