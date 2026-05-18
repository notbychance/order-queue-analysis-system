import pytest

from app.schemas.queue import QueueAnalysisRequest
from app.services.queue_analysis import analyze_queue


def test_analyze_variant_17_returns_expected_values() -> None:
    request = QueueAnalysisRequest(lambda_rate=6, mu_rate=8)

    result = analyze_queue(request)

    assert result.is_stable is True
    assert result.rho == pytest.approx(0.75)
    assert result.average_orders_in_system == pytest.approx(3.0)
    assert result.average_waiting_time == pytest.approx(0.375)
    assert result.average_time_in_system == pytest.approx(0.5)


def test_analyze_zero_arrival_rate_returns_no_queue() -> None:
    request = QueueAnalysisRequest(lambda_rate=0, mu_rate=8)

    result = analyze_queue(request)

    assert result.is_stable is True
    assert result.rho == pytest.approx(0.0)
    assert result.average_orders_in_system == pytest.approx(0.0)
    assert result.average_waiting_time == pytest.approx(0.0)
    assert result.average_time_in_system == pytest.approx(0.125)


def test_analyze_equal_rates_returns_unstable_system() -> None:
    request = QueueAnalysisRequest(lambda_rate=8, mu_rate=8)

    result = analyze_queue(request)

    assert result.is_stable is False
    assert result.rho == pytest.approx(1.0)
    assert result.average_orders_in_system is None
    assert result.average_waiting_time is None
    assert result.average_time_in_system is None


def test_analyze_arrival_rate_greater_than_service_rate_returns_unstable_system() -> None:
    request = QueueAnalysisRequest(lambda_rate=10, mu_rate=8)

    result = analyze_queue(request)

    assert result.is_stable is False
    assert result.rho == pytest.approx(1.25)
    assert result.average_orders_in_system is None
    assert result.average_waiting_time is None
    assert result.average_time_in_system is None
