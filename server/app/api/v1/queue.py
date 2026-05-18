from fastapi import APIRouter

from app.schemas.queue import (
    QueueAnalysisRequest,
    QueueAnalysisResponse,
    QueueFormulasResponse,
)
from app.services.queue_analysis import analyze_queue_system


router = APIRouter(
    prefix="/queue",
    tags=["queue-analysis"],
)


@router.post(
    "/analyze",
    response_model=QueueAnalysisResponse,
    summary="Выполнить анализ системы M/M/1",
    description=(
        "Принимает интенсивность поступления заказов `λ` и интенсивность "
        "обслуживания `μ`. Возвращает коэффициент загрузки, среднее число "
        "заказов в системе, среднее время ожидания и среднее время пребывания "
        "заказа в системе. Если `λ >= μ`, система считается неустойчивой, а "
        "стационарные показатели возвращаются как `null`."
    ),
    response_description="Результат анализа системы массового обслуживания.",
    responses={
        200: {
            "description": "Расчет выполнен успешно.",
            "content": {
                "application/json": {
                    "examples": {
                        "stable": {
                            "summary": "Устойчивая система",
                            "description": "Пример расчета при λ = 6, μ = 8.",
                            "value": {
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
                                "conclusion": (
                                    "Система устойчива. Клерк загружен на 75.0%. "
                                    "Очередь не растет неограниченно."
                                ),
                            },
                        },
                        "unstable": {
                            "summary": "Неустойчивая система",
                            "description": "Пример расчета при λ = μ.",
                            "value": {
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
                                "conclusion": (
                                    "Система неустойчива: интенсивность поступления "
                                    "заказов больше или равна интенсивности "
                                    "обслуживания. Очередь будет расти неограниченно."
                                ),
                            },
                        },
                    }
                }
            },
        },
        422: {
            "description": (
                "Ошибка валидации входных параметров. Например, `lambda_rate < 0` "
                "или `mu_rate <= 0`."
            ),
        },
    },
)
def analyze_queue(
    request: QueueAnalysisRequest,
) -> QueueAnalysisResponse:
    return analyze_queue_system(request)


@router.get(
    "/formulas",
    response_model=QueueFormulasResponse,
    summary="Получить формулы модели M/M/1",
    description=(
        "Возвращает описание математической модели, условие устойчивости и "
        "формулы, используемые при анализе одноканальной системы массового "
        "обслуживания."
    ),
    response_description="Описание модели и формулы расчета.",
    responses={
        200: {
            "description": "Формулы успешно получены.",
            "content": {
                "application/json": {
                    "example": {
                        "model_name": "M/M/1",
                        "description": (
                            "Одноканальная система массового обслуживания с "
                            "пуассоновским потоком заявок и экспоненциальным "
                            "временем обслуживания."
                        ),
                        "stability_condition": "λ < μ",
                        "formulas": {
                            "utilization": "ρ = λ / μ",
                            "average_orders_in_system": "L = λ / (μ - λ)",
                            "average_waiting_time": "Wq = λ / (μ * (μ - λ))",
                            "average_time_in_system": "W = 1 / (μ - λ)",
                        },
                    }
                }
            },
        }
    },
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
            "utilization": "ρ = λ / μ",
            "average_orders_in_system": "L = λ / (μ - λ)",
            "average_waiting_time": "Wq = λ / (μ * (μ - λ))",
            "average_time_in_system": "W = 1 / (μ - λ)",
        },
    )
