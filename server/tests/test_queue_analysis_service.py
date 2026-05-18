import pytest

from app.schemas.queue import QueueAnalysisRequest
from app.services.queue_analysis import analyze_queue


def test_analyze_variant_17_returns_expected_values() -> None:
    request = QueueAnalysisRequest(lambda_rate=6, mu_rate=8)

    result = analyze_queue(request)

    assert result.is_stable is True
    assert result.rho == pytest.approx(0.75)
    assert result.utilization_percent == pytest.approx(75.0)
    assert result.average_orders_in_system == pytest.approx(3.0)
    assert result.average_waiting_time == pytest.approx(0.375)
    assert result.average_time_in_system == pytest.approx(0.5)
    assert result.average_waiting_time_hours == pytest.approx(9.0)
    assert result.average_time_in_system_hours == pytest.approx(12.0)
    assert result.rate_unit_label == "заказов/день"
    assert result.time_unit_label == "дней"
    assert "Система работает устойчиво" in result.conclusion


def test_analyze_zero_arrival_rate_returns_no_queue() -> None:
    request = QueueAnalysisRequest(lambda_rate=0, mu_rate=8)

    result = analyze_queue(request)

    assert result.is_stable is True
    assert result.rho == pytest.approx(0.0)
    assert result.utilization_percent == pytest.approx(0.0)
    assert result.average_orders_in_system == pytest.approx(0.0)
    assert result.average_waiting_time == pytest.approx(0.0)
    assert result.average_time_in_system == pytest.approx(0.125)
    assert result.average_waiting_time_hours == pytest.approx(0.0)
    assert result.average_time_in_system_hours == pytest.approx(3.0)


def test_analyze_equal_rates_returns_unstable_system() -> None:
    request = QueueAnalysisRequest(lambda_rate=8, mu_rate=8)

    result = analyze_queue(request)

    assert result.is_stable is False
    assert result.rho == pytest.approx(1.0)
    assert result.utilization_percent == pytest.approx(100.0)
    assert result.average_orders_in_system is None
    assert result.average_waiting_time is None
    assert result.average_time_in_system is None
    assert result.average_waiting_time_hours is None
    assert result.average_time_in_system_hours is None
    assert "Система неустойчива" in result.conclusion


def test_analyze_arrival_rate_greater_than_service_rate_returns_unstable_system() -> None:
    request = QueueAnalysisRequest(lambda_rate=10, mu_rate=8)

    result = analyze_queue(request)

    assert result.is_stable is False
    assert result.rho == pytest.approx(1.25)
    assert result.utilization_percent == pytest.approx(125.0)
    assert result.average_orders_in_system is None
    assert result.average_waiting_time is None
    assert result.average_time_in_system is None
    assert result.average_waiting_time_hours is None
    assert result.average_time_in_system_hours is None
