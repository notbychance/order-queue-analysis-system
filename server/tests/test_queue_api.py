import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_get_default_queue_params() -> None:
    response = client.get("/api/v1/queue/default")

    assert response.status_code == 200
    data = response.json()
    assert data["lambda_rate"] == 6
    assert data["mu_rate"] == 8


def test_analyze_queue_endpoint_returns_expected_result() -> None:
    response = client.post(
        "/api/v1/queue/analyze",
        json={"lambda_rate": 6, "mu_rate": 8},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["is_stable"] is True
    assert data["rho"] == pytest.approx(0.75)
    assert data["average_orders_in_system"] == pytest.approx(3.0)
    assert data["average_waiting_time"] == pytest.approx(0.375)
    assert data["average_time_in_system"] == pytest.approx(0.5)


def test_analyze_queue_endpoint_returns_unstable_result() -> None:
    response = client.post(
        "/api/v1/queue/analyze",
        json={"lambda_rate": 8, "mu_rate": 8},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["is_stable"] is False
    assert data["rho"] == pytest.approx(1.0)
    assert data["average_orders_in_system"] is None
    assert data["average_waiting_time"] is None
    assert data["average_time_in_system"] is None


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
