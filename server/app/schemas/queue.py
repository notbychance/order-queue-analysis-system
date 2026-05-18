from pydantic import BaseModel, Field


class QueueAnalysisRequest(BaseModel):
    lambda_rate: float = Field(
        ge=0,
        description="Интенсивность поступления заказов, λ, заказов в день",
        examples=[6],
    )
    mu_rate: float = Field(
        gt=0,
        description="Интенсивность обслуживания заказов, μ, заказов в день",
        examples=[8],
    )


class QueueAnalysisResponse(BaseModel):
    lambda_rate: float = Field(description="Интенсивность поступления заказов, λ")
    mu_rate: float = Field(description="Интенсивность обслуживания заказов, μ")

    rate_unit: str = Field(
        default="orders_per_day",
        description="Единица измерения интенсивностей",
    )
    rate_unit_label: str = Field(
        default="заказов/день",
        description="Человекочитаемая единица измерения интенсивностей",
    )
    time_unit: str = Field(
        default="days",
        description="Базовая единица измерения времени в расчетах",
    )
    time_unit_label: str = Field(
        default="дней",
        description="Человекочитаемая базовая единица измерения времени",
    )

    rho: float = Field(description="Коэффициент загрузки клерка, ρ = λ / μ")
    utilization_percent: float = Field(description="Загрузка клерка в процентах")
    is_stable: bool = Field(description="Признак устойчивости системы: λ < μ")

    average_orders_in_system: float | None = Field(
        default=None,
        description="Среднее число заказов в системе, L",
    )
    average_waiting_time: float | None = Field(
        default=None,
        description="Среднее время ожидания начала обслуживания, Wq, дней",
    )
    average_time_in_system: float | None = Field(
        default=None,
        description="Среднее время пребывания заказа в системе, W, дней",
    )

    average_waiting_time_hours: float | None = Field(
        default=None,
        description="Среднее время ожидания начала обслуживания, Wq, часов",
    )
    average_time_in_system_hours: float | None = Field(
        default=None,
        description="Среднее время пребывания заказа в системе, W, часов",
    )

    message: str = Field(description="Краткое техническое сообщение о результате расчета")
    conclusion: str = Field(description="Человекочитаемое заключение для отображения в клиентах")
