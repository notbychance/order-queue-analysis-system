from __future__ import annotations

from pydantic import BaseModel, Field


class QueueAnalysisRequest(BaseModel):
    """DTO запроса анализа системы массового обслуживания."""

    lambda_rate: float = Field(
        ge=0,
        description="Интенсивность поступления заказов λ, заказов в день",
    )

    mu_rate: float = Field(
        gt=0,
        description="Интенсивность обслуживания заказов μ, заказов в день",
    )


class QueueAnalysisResponse(BaseModel):
    """DTO ответа FastAPI с результатами анализа системы M/M/1."""

    lambda_rate: float = Field(
        description="Интенсивность поступления заказов λ",
    )

    mu_rate: float = Field(
        description="Интенсивность обслуживания заказов μ",
    )

    arrival_rate_unit: str = Field(
        default="заказов/день",
        description="Единица измерения интенсивности поступления",
    )

    service_rate_unit: str = Field(
        default="заказов/день",
        description="Единица измерения интенсивности обслуживания",
    )

    time_unit: str = Field(
        default="дней",
        description="Единица измерения времени",
    )

    is_stable: bool = Field(
        description="Признак устойчивости системы",
    )

    utilization: float = Field(
        description="Коэффициент загрузки клерка ρ",
    )

    utilization_percent: float = Field(
        description="Коэффициент загрузки клерка в процентах",
    )

    average_orders_in_system: float | None = Field(
        default=None,
        description="Среднее число заказов в системе L",
    )

    average_waiting_time: float | None = Field(
        default=None,
        description="Среднее время ожидания начала обработки Wq, дней",
    )

    average_waiting_time_hours: float | None = Field(
        default=None,
        description="Среднее время ожидания начала обработки Wq, часов",
    )

    average_time_in_system: float | None = Field(
        default=None,
        description="Среднее время пребывания заказа в системе W, дней",
    )

    average_time_in_system_hours: float | None = Field(
        default=None,
        description="Среднее время пребывания заказа в системе W, часов",
    )

    conclusion: str = Field(
        description="Текстовое заключение по результатам анализа",
    )


class QueueFormulasResponse(BaseModel):
    """DTO ответа FastAPI с формулами модели M/M/1."""

    model_name: str = Field(
        description="Название модели массового обслуживания",
    )

    description: str = Field(
        description="Описание модели",
    )

    stability_condition: str = Field(
        description="Условие устойчивости системы",
    )

    formulas: dict[str, str] = Field(
        description="Список используемых формул",
    )
