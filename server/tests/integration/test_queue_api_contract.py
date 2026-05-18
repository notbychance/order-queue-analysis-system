from __future__ import annotations

import math

import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

ANALYZE_RESPONSE_FIELDS = {
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

DEPRECATED_RESPONSE_FIELDS = {
    "rho",
    "rate_unit",
    "rate_unit_label",
    "time_unit_label",
    "message",
}


@pytest.mark.integration
def test_analyze_endpoint_returns_client_contract_for_stable_system():
    response = client.post(
        "/api/v1/queue/analyze",
        json={
            "lambda_rate": 6,
            "mu_rate": 8,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert set(data.keys()) == ANALYZE_RESPONSE_FIELDS
    assert DEPRECATED_RESPONSE_FIELDS.isdisjoint(data.keys())

    assert data["lambda_rate"] == 6.0
    assert data["mu_rate"] == 8.0
    assert data["arrival_rate_unit"] == "заказов/день"
    assert data["service_rate_unit"] == "заказов/день"
    assert data["time_unit"] == "дней"

    assert data["is_stable"] is True
    assert math.isclose(data["utilization"], 0.75)
    assert math.isclose(data["utilization_percent"], 75.0)

    assert math.isclose(data["average_orders_in_system"], 3.0)
    assert math.isclose(data["average_waiting_time"], 0.375)
    assert math.isclose(data["average_waiting_time_hours"], 9.0)
    assert math.isclose(data["average_time_in_system"], 0.5)
    assert math.isclose(data["average_time_in_system_hours"], 12.0)

    assert "устойчива" in data["conclusion"].lower()


@pytest.mark.integration
def test_analyze_endpoint_returns_client_contract_for_unstable_system():
    response = client.post(
        "/api/v1/queue/analyze",
        json={
            "lambda_rate": 8,
            "mu_rate": 8,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert set(data.keys()) == ANALYZE_RESPONSE_FIELDS
    assert DEPRECATED_RESPONSE_FIELDS.isdisjoint(data.keys())

    assert data["is_stable"] is False
    assert math.isclose(data["utilization"], 1.0)
    assert math.isclose(data["utilization_percent"], 100.0)

    assert data["average_orders_in_system"] is None
    assert data["average_waiting_time"] is None
    assert data["average_waiting_time_hours"] is None
    assert data["average_time_in_system"] is None
    assert data["average_time_in_system_hours"] is None

    assert "неустойчива" in data["conclusion"].lower()


@pytest.mark.integration
def test_formulas_endpoint_uses_same_field_names_as_clients():
    response = client.get("/api/v1/queue/formulas")

    assert response.status_code == 200

    data = response.json()
    formulas = data["formulas"]

    assert data["model_name"] == "M/M/1"
    assert data["stability_condition"] == "λ < μ"

    assert "utilization" in formulas
    assert "average_orders_in_system" in formulas
    assert "average_waiting_time" in formulas
    assert "average_time_in_system" in formulas

    assert "rho" not in formulas


@pytest.mark.integration
def test_removed_default_endpoint_is_not_available():
    response = client.get("/api/v1/queue/default")

    assert response.status_code == 404
