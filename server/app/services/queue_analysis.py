from app.schemas.queue import QueueAnalysisRequest, QueueAnalysisResponse


ROUND_DIGITS = 6


def analyze_queue(request: QueueAnalysisRequest) -> QueueAnalysisResponse:
    """Analyze a single-server M/M/1 queueing system.

    The function does not store history. It only calculates the current result
    for the received parameters. Calculation history is kept locally by clients.
    """

    lambda_rate = request.lambda_rate
    mu_rate = request.mu_rate
    rho = lambda_rate / mu_rate

    if lambda_rate >= mu_rate:
        return QueueAnalysisResponse(
            lambda_rate=lambda_rate,
            mu_rate=mu_rate,
            rho=round(rho, ROUND_DIGITS),
            is_stable=False,
            average_orders_in_system=None,
            average_waiting_time=None,
            average_time_in_system=None,
            message=(
                "Система неустойчива: интенсивность поступления заказов "
                "должна быть меньше интенсивности обслуживания."
            ),
        )

    denominator = mu_rate - lambda_rate

    average_orders_in_system = lambda_rate / denominator
    average_waiting_time = lambda_rate / (mu_rate * denominator)
    average_time_in_system = 1 / denominator

    return QueueAnalysisResponse(
        lambda_rate=lambda_rate,
        mu_rate=mu_rate,
        rho=round(rho, ROUND_DIGITS),
        is_stable=True,
        average_orders_in_system=round(average_orders_in_system, ROUND_DIGITS),
        average_waiting_time=round(average_waiting_time, ROUND_DIGITS),
        average_time_in_system=round(average_time_in_system, ROUND_DIGITS),
        message="Система устойчива, расчет выполнен успешно.",
    )
