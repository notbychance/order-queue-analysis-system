from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class HistoryCreate(BaseModel):
    """DTO для создания локальной записи истории расчета."""

    created_at: datetime | None = Field(
        default=None,
        description="Дата и время создания записи. Если не передано, задается автоматически.",
    )

    lambda_rate: float = Field(
        ge=0,
        description="Интенсивность поступления заказов λ",
    )

    mu_rate: float = Field(
        gt=0,
        description="Интенсивность обслуживания заказов μ",
    )

    is_stable: bool = Field(
        description="Признак устойчивости системы",
    )

    utilization: float = Field(
        ge=0,
        description="Коэффициент загрузки клерка ρ",
    )

    utilization_percent: float = Field(
        ge=0,
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
        min_length=1,
        description="Текстовое заключение по результатам анализа",
    )


class HistoryItem(HistoryCreate):
    """DTO локальной записи истории расчета."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(
        description="Идентификатор записи истории",
    )

    created_at: datetime = Field(
        description="Дата и время создания записи",
    )
