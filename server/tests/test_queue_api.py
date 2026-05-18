import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


CLIENT_CONTRACT_FIELDS = {
    "lambda_rate",
    "mu_rate",
    "arrival_rate_unit",
    "service_rate_unit",
    "time_unit",
    "is_stable",
    "utilization",
    "utilization_percent",
    "average_orders_in_system",
    "average_waiting_time",
    "average_waiting_time_hours",
    "average_time_in_system",
    "average_time_in_system_hours",
    "conclusion",
}

OBSOLETE_CONTRACT_FIELDS = {
    "rho",
    "rate_unit",
    "rate_unit_label",
    "time_unit_label",
    "message",
}


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_get_default_queue_params_endpoint_is_removed() -> None:
    response = client.get("/api/v1/queue/default")

    assert response.status_code == 404


def test_get_queue_formulas() -> None:
    response = client.get("/api/v1/queue/formulas")

    assert response.status_code == 200
    data = response.json()
    assert data["model_name"] == "M/M/1"
    assert data["stability_condition"] == "λ < μ"
    assert data["formulas"]["utilization"] == "ρ = λ / μ"
    assert "rho" not in data["formulas"]
    assert "average_orders_in_system" in data["formulas"]
    assert "average_waiting_time" in data["formulas"]
    assert "average_time_in_system" in data["formulas"]


def test_analyze_queue_endpoint_returns_client_contract_fields() -> None:
    response = client.post(
        "/api/v1/queue/analyze",
        json={"lambda_rate": 6, "mu_rate": 8},
    )

    assert response.status_code == 200
    data = response.json()
    assert CLIENT_CONTRACT_FIELDS.issubset(data.keys())
    assert OBSOLETE_CONTRACT_FIELDS.isdisjoint(data.keys())


def test_analyze_queue_endpoint_returns_expected_result() -> None:
    response = client.post(
        "/api/v1/queue/analyze",
        json={"lambda_rate": 6, "mu_rate": 8},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["is_stable"] is True
    assert data["utilization"] == pytest.approx(0.75)
    assert data["utilization_percent"] == pytest.approx(75.0)
    assert data["average_orders_in_system"] == pytest.approx(3.0)
    assert data["average_waiting_time"] == pytest.approx(0.375)
    assert data["average_time_in_system"] == pytest.approx(0.5)
    assert data["average_waiting_time_hours"] == pytest.approx(9.0)
    assert data["average_time_in_system_hours"] == pytest.approx(12.0)
    assert data["arrival_rate_unit"] == "заказов/день"
    assert data["service_rate_unit"] == "заказов/день"
    assert data["time_unit"] == "дней"
    assert "Система работает устойчиво" in data["conclusion"]


def test_analyze_queue_endpoint_returns_unstable_result() -> None:
    response = client.post(
        "/api/v1/queue/analyze",
        json={"lambda_rate": 8, "mu_rate": 8},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["is_stable"] is False
    assert data["utilization"] == pytest.approx(1.0)
    assert data["utilization_percent"] == pytest.approx(100.0)
    assert data["average_orders_in_system"] is None
    assert data["average_waiting_time"] is None
    assert data["average_time_in_system"] is None
    assert data["average_waiting_time_hours"] is None
    assert data["average_time_in_system_hours"] is None
    assert "Система неустойчива" in data["conclusion"]


def test_analyze_queue_endpoint_rejects_negative_lambda_rate() -> None:
    response = client.post(
        "/api/v1/queue/analyze",
        json={"lambda_rate": -1, "mu_rate": 8},
    )

    assert response.status_code == 422


def test_analyze_queue_endpoint_rejects_zero_mu_rate() -> None:
    response = client.post(
        "/api/v1/queue/analyze",
        json={"lambda_rate": 6, "mu_rate": 0},
    )

    assert response.status_code == 422


def test_analyze_queue_endpoint_rejects_string_values() -> None:
    response = client.post(
        "/api/v1/queue/analyze",
        json={"lambda_rate": "abc", "mu_rate": 8},
    )

    assert response.status_code == 422
