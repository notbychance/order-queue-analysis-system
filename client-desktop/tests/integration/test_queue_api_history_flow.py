from __future__ import annotations

import httpx
import pytest

from app.api.queue_api_client import QueueApiClient
from app.data.repositories.history_repository import HistoryRepository
from app.data.sqlalchemy_connection_manager import SQLAlchemyConnectionManager
from app.schemas.history import HistoryCreate
from app.schemas.queue import QueueAnalysisRequest, QueueAnalysisResponse
from app.services.history_service import HistoryService


API_BASE_URL = "http://testserver/api/v1"


def stable_server_response() -> dict:
    return {
        "lambda_rate": 6.0,
        "mu_rate": 8.0,
        "arrival_rate_unit": "заказов/день",
        "service_rate_unit": "заказов/день",
        "time_unit": "дней",
        "is_stable": True,
        "utilization": 0.75,
        "utilization_percent": 75.0,
        "average_orders_in_system": 3.0,
        "average_waiting_time": 0.375,
        "average_waiting_time_hours": 9.0,
        "average_time_in_system": 0.5,
        "average_time_in_system_hours": 12.0,
        "conclusion": "Система устойчива. Клерк загружен на 75.0%. Очередь не растет неограниченно.",
    }


def unstable_server_response() -> dict:
    return {
        "lambda_rate": 8.0,
        "mu_rate": 8.0,
        "arrival_rate_unit": "заказов/день",
        "service_rate_unit": "заказов/день",
        "time_unit": "дней",
        "is_stable": False,
        "utilization": 1.0,
        "utilization_percent": 100.0,
        "average_orders_in_system": None,
        "average_waiting_time": None,
        "average_waiting_time_hours": None,
        "average_time_in_system": None,
        "average_time_in_system_hours": None,
        "conclusion": "Система неустойчива: очередь будет расти неограниченно.",
    }


def formulas_server_response() -> dict:
    return {
        "model_name": "M/M/1",
        "description": "Одноканальная система массового обслуживания.",
        "stability_condition": "λ < μ",
        "formulas": {
            "utilization": "ρ = λ / μ",
            "average_orders_in_system": "L = λ / (μ - λ)",
            "average_waiting_time": "Wq = λ / (μ * (μ - λ))",
            "average_time_in_system": "W = 1 / (μ - λ)",
        },
    }


def create_api_client(*, analyze_payload: dict) -> QueueApiClient:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "POST" and request.url.path == "/api/v1/queue/analyze":
            return httpx.Response(200, json=analyze_payload)

        if request.method == "GET" and request.url.path == "/api/v1/queue/formulas":
            return httpx.Response(200, json=formulas_server_response())

        return httpx.Response(404, json={"detail": "Not found"})

    http_client = httpx.Client(
        base_url=API_BASE_URL,
        transport=httpx.MockTransport(handler),
    )

    return QueueApiClient(
        base_url=API_BASE_URL,
        client=http_client,
    )


def create_history_service(tmp_path) -> HistoryService:
    manager = SQLAlchemyConnectionManager(tmp_path / "history.sqlite3")
    repository = HistoryRepository(manager, max_items=50)
    service = HistoryService(repository)
    service.initialize()
    return service


def history_create_from_response(response: QueueAnalysisResponse) -> HistoryCreate:
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


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.data
def test_desktop_api_response_can_be_saved_to_local_sqlite_history(tmp_path):
    api_client = create_api_client(analyze_payload=stable_server_response())
    history_service = create_history_service(tmp_path)

    response = api_client.analyze_queue(
        QueueAnalysisRequest(lambda_rate=6.0, mu_rate=8.0)
    )
    saved_item = history_service.add_history_item(
        history_create_from_response(response)
    )

    assert history_service.count_history_items() == 1

    loaded_item = history_service.get_history_item(saved_item.id)

    assert loaded_item is not None
    assert loaded_item.lambda_rate == 6.0
    assert loaded_item.mu_rate == 8.0
    assert loaded_item.is_stable is True
    assert loaded_item.utilization == 0.75
    assert loaded_item.utilization_percent == 75.0
    assert loaded_item.average_orders_in_system == 3.0
    assert loaded_item.average_waiting_time_hours == 9.0
    assert loaded_item.average_time_in_system_hours == 12.0
    assert "устойчива" in loaded_item.conclusion.lower()


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.data
def test_desktop_api_response_saves_unstable_result_with_empty_metrics(tmp_path):
    api_client = create_api_client(analyze_payload=unstable_server_response())
    history_service = create_history_service(tmp_path)

    response = api_client.analyze_queue(
        QueueAnalysisRequest(lambda_rate=8.0, mu_rate=8.0)
    )
    saved_item = history_service.add_history_item(
        history_create_from_response(response)
    )

    loaded_item = history_service.get_history_item(saved_item.id)

    assert loaded_item is not None
    assert loaded_item.is_stable is False
    assert loaded_item.utilization == 1.0
    assert loaded_item.average_orders_in_system is None
    assert loaded_item.average_waiting_time is None
    assert loaded_item.average_time_in_system is None


@pytest.mark.integration
@pytest.mark.api
def test_desktop_formulas_api_uses_current_contract_names():
    api_client = create_api_client(analyze_payload=stable_server_response())

    formulas = api_client.get_formulas()

    assert formulas.model_name == "M/M/1"
    assert "utilization" in formulas.formulas
    assert "rho" not in formulas.formulas
