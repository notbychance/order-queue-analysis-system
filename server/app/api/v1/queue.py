from fastapi import APIRouter

from app.schemas.queue import (
    QueueAnalysisRequest,
    QueueAnalysisResponse,
    QueueFormulasResponse,
)
from app.services.queue_analysis import analyze_queue


router = APIRouter(prefix="/queue", tags=["queue-analysis"])


@router.post(
    "/analyze",
    response_model=QueueAnalysisResponse,
    summary="Выполнить анализ системы массового обслуживания",
    description=(
        "Принимает интенсивность поступления заказов λ и интенсивность "
        "обслуживания μ. Возвращает коэффициент загрузки, среднее число "
        "заказов в системе, среднее время ожидания и среднее время пребывания "
        "заказа в системе. История расчетов на сервере не сохраняется."
    ),
)
def analyze_queue_system(request: QueueAnalysisRequest) -> QueueAnalysisResponse:
    return analyze_queue(request)


@router.get(
    "/formulas",
    response_model=QueueFormulasResponse,
    summary="Получить формулы модели M/M/1",
    description=(
        "Возвращает описание математической модели и формулы, используемые "
        "при анализе одноканальной системы массового обслуживания."
    ),
)
def get_queue_formulas() -> QueueFormulasResponse:
    return QueueFormulasResponse(
        model_name="M/M/1",
        description=(
            "Одноканальная система массового обслуживания с пуассоновским "
            "потоком заявок и экспоненциальным временем обслуживания."
        ),
        stability_condition="λ < μ",
        formulas={
            "rho": "ρ = λ / μ",
            "average_orders_in_system": "L = λ / (μ - λ)",
            "average_waiting_time": "Wq = λ / (μ * (μ - λ))",
            "average_time_in_system": "W = 1 / (μ - λ)",
        },
    )
