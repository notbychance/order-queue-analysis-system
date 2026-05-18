from pydantic import BaseModel, Field


class QueueAnalysisRequest(BaseModel):
    lambda_rate: float = Field(
        ge=0,
        description="Интенсивность поступления заказов λ, заказов в день",
        examples=[6],
    )
    mu_rate: float = Field(
        gt=0,
        description="Интенсивность обслуживания заказов μ, заказов в день",
        examples=[8],
    )


class QueueAnalysisResponse(BaseModel):
    """DTO ответа FastAPI, общий для web- и desktop-клиентов."""

    lambda_rate: float = Field(description="Интенсивность поступления заказов λ")
    mu_rate: float = Field(description="Интенсивность обслуживания заказов μ")

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

    is_stable: bool = Field(description="Признак устойчивости системы: λ < μ")

    utilization: float = Field(description="Коэффициент загрузки клерка, ρ = λ / μ")
    utilization_percent: float = Field(description="Загрузка клерка в процентах")

    average_orders_in_system: float | None = Field(
        default=None,
        description="Среднее число заказов в системе, L",
    )
    average_waiting_time: float | None = Field(
        default=None,
        description="Среднее время ожидания начала обслуживания, Wq, дней",
    )
    average_waiting_time_hours: float | None = Field(
        default=None,
        description="Среднее время ожидания начала обслуживания, Wq, часов",
    )
    average_time_in_system: float | None = Field(
        default=None,
        description="Среднее время пребывания заказа в системе, W, дней",
    )
    average_time_in_system_hours: float | None = Field(
        default=None,
        description="Среднее время пребывания заказа в системе, W, часов",
    )

    conclusion: str = Field(description="Человекочитаемое заключение для отображения в клиентах")


class QueueFormulasResponse(BaseModel):
    model_name: str = Field(description="Название модели массового обслуживания")
    description: str = Field(description="Описание модели")
    stability_condition: str = Field(description="Условие устойчивости системы")
    formulas: dict[str, str] = Field(description="Список используемых формул")
