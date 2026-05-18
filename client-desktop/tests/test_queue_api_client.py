from __future__ import annotations

from dataclasses import replace

import httpx
import pytest
import respx

from app.api.errors import QueueApiConnectionError, QueueApiResponseError
from app.api.queue_api_client import QueueApiClient, create_queue_api_client
from app.core.settings import get_settings
from app.schemas.queue import QueueAnalysisRequest, QueueAnalysisResponse


API_BASE_URL = "http://testserver/api/v1"


def make_analysis_response() -> dict:
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
        "conclusion": "Система устойчива.",
    }


@pytest.mark.unit
@pytest.mark.api
@respx.mock
def test_analyze_queue_sends_request_and_returns_response():
    route = respx.post(f"{API_BASE_URL}/queue/analyze").mock(
        return_value=httpx.Response(200, json=make_analysis_response())
    )
    client = QueueApiClient(API_BASE_URL)

    result = client.analyze_queue(
        QueueAnalysisRequest(lambda_rate=6.0, mu_rate=8.0)
    )

    assert isinstance(result, QueueAnalysisResponse)
    assert result.lambda_rate == 6.0
    assert result.mu_rate == 8.0
    assert result.is_stable is True
    assert result.utilization_percent == 75.0

    assert route.called
    assert route.calls.last is not None
    assert route.calls.last.request.content == b'{"lambda_rate":6.0,"mu_rate":8.0}'


@pytest.mark.unit
@pytest.mark.api
@respx.mock
def test_get_formulas_returns_response():
    respx.get(f"{API_BASE_URL}/queue/formulas").mock(
        return_value=httpx.Response(
            200,
            json={
                "model_name": "M/M/1",
                "description": "Одноканальная система массового обслуживания.",
                "stability_condition": "λ < μ",
                "formulas": {
                    "utilization": "ρ = λ / μ",
                    "average_orders_in_system": "L = λ / (μ - λ)",
                },
            },
        )
    )
    client = QueueApiClient(API_BASE_URL)

    formulas = client.get_formulas()

    assert formulas.model_name == "M/M/1"
    assert formulas.stability_condition == "λ < μ"
    assert formulas.formulas["utilization"] == "ρ = λ / μ"


@pytest.mark.unit
@pytest.mark.api
@respx.mock
def test_health_check_uses_server_root_url():
    route = respx.get("http://testserver/health").mock(
        return_value=httpx.Response(
            200,
            json={
                "status": "ok",
                "service": "Queue Analysis API",
                "environment": "development",
            },
        )
    )
    client = QueueApiClient(API_BASE_URL)

    result = client.health_check()

    assert result["status"] == "ok"
    assert route.called


@pytest.mark.unit
@pytest.mark.api
@respx.mock
def test_analyze_queue_raises_response_error_for_validation_error():
    respx.post(f"{API_BASE_URL}/queue/analyze").mock(
        return_value=httpx.Response(
            422,
            json={
                "detail": [
                    {
                        "type": "greater_than",
                        "loc": ["body", "mu_rate"],
                        "msg": "Input should be greater than 0",
                    }
                ]
            },
        )
    )
    client = QueueApiClient(API_BASE_URL)

    with pytest.raises(QueueApiResponseError) as exc_info:
        client.analyze_queue(QueueAnalysisRequest(lambda_rate=6.0, mu_rate=8.0))

    assert exc_info.value.status_code == 422
    assert "валидации" in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.api
@respx.mock
def test_analyze_queue_raises_connection_error_on_timeout():
    respx.post(f"{API_BASE_URL}/queue/analyze").mock(
        side_effect=httpx.ConnectError("connection failed")
    )
    client = QueueApiClient(API_BASE_URL)

    with pytest.raises(QueueApiConnectionError):
        client.analyze_queue(QueueAnalysisRequest(lambda_rate=6.0, mu_rate=8.0))


@pytest.mark.unit
@pytest.mark.api
@respx.mock
def test_analyze_queue_raises_response_error_for_invalid_response_schema():
    respx.post(f"{API_BASE_URL}/queue/analyze").mock(
        return_value=httpx.Response(200, json={"unexpected": "data"})
    )
    client = QueueApiClient(API_BASE_URL)

    with pytest.raises(QueueApiResponseError) as exc_info:
        client.analyze_queue(QueueAnalysisRequest(lambda_rate=6.0, mu_rate=8.0))

    assert exc_info.value.status_code == 200
    assert "неизвестном формате" in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.api
def test_create_queue_api_client_uses_settings(tmp_path):
    settings = replace(
        get_settings(),
        api_base_url="http://example.test/api/v1",
        request_timeout_seconds=3.0,
        sqlite_database_path=tmp_path / "history.sqlite3",
    )

    client = create_queue_api_client(settings)

    assert client.base_url == "http://example.test/api/v1"
    assert client.timeout_seconds == 3.0
    client.close()
