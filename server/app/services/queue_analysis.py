from app.schemas.queue import QueueAnalysisRequest, QueueAnalysisResponse


ROUND_DIGITS = 6
HOURS_IN_DAY = 24
RATE_UNIT_LABEL = "заказов/день"
TIME_UNIT_LABEL = "дней"


def _round(value: float) -> float:
    return round(value, ROUND_DIGITS)


def analyze_queue(request: QueueAnalysisRequest) -> QueueAnalysisResponse:
    """Analyze a single-server M/M/1 queueing system.

    The function does not store history. It only calculates the current result
    for the received parameters. Calculation history is kept locally by clients.

    Input rates are interpreted as orders per day. Therefore calculated time
    values are returned both in days and in hours.
    """

    lambda_rate = request.lambda_rate
    mu_rate = request.mu_rate
    utilization = lambda_rate / mu_rate
    utilization_percent = utilization * 100

    if lambda_rate >= mu_rate:
        rounded_utilization = _round(utilization)
        rounded_percent = _round(utilization_percent)

        return QueueAnalysisResponse(
            lambda_rate=lambda_rate,
            mu_rate=mu_rate,
            arrival_rate_unit=RATE_UNIT_LABEL,
            service_rate_unit=RATE_UNIT_LABEL,
            time_unit=TIME_UNIT_LABEL,
            is_stable=False,
            utilization=rounded_utilization,
            utilization_percent=rounded_percent,
            average_orders_in_system=None,
            average_waiting_time=None,
            average_waiting_time_hours=None,
            average_time_in_system=None,
            average_time_in_system_hours=None,
            conclusion=(
                f"Клерк загружен на {rounded_percent}%. Система неустойчива: "
                "очередь будет расти, поэтому расчет средних показателей "
                "для установившегося режима невозможен."
            ),
        )

    denominator = mu_rate - lambda_rate

    average_orders_in_system = lambda_rate / denominator
    average_waiting_time = lambda_rate / (mu_rate * denominator)
    average_time_in_system = 1 / denominator

    average_waiting_time_hours = average_waiting_time * HOURS_IN_DAY
    average_time_in_system_hours = average_time_in_system * HOURS_IN_DAY

    rounded_utilization = _round(utilization)
    rounded_percent = _round(utilization_percent)
    rounded_orders = _round(average_orders_in_system)
    rounded_waiting_days = _round(average_waiting_time)
    rounded_waiting_hours = _round(average_waiting_time_hours)
    rounded_system_days = _round(average_time_in_system)
    rounded_system_hours = _round(average_time_in_system_hours)

    return QueueAnalysisResponse(
        lambda_rate=lambda_rate,
        mu_rate=mu_rate,
        arrival_rate_unit=RATE_UNIT_LABEL,
        service_rate_unit=RATE_UNIT_LABEL,
        time_unit=TIME_UNIT_LABEL,
        is_stable=True,
        utilization=rounded_utilization,
        utilization_percent=rounded_percent,
        average_orders_in_system=rounded_orders,
        average_waiting_time=rounded_waiting_days,
        average_waiting_time_hours=rounded_waiting_hours,
        average_time_in_system=rounded_system_days,
        average_time_in_system_hours=rounded_system_hours,
        conclusion=(
            f"Клерк загружен на {rounded_percent}%. Система работает устойчиво. "
            f"В среднем в системе находится {rounded_orders} заказов, "
            f"ожидание начала обработки составляет {rounded_waiting_hours} ч., "
            f"а полное время пребывания заказа в системе — {rounded_system_hours} ч."
        ),
    )
