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
    lambda_rate: float
    mu_rate: float
    rho: float = Field(description="Коэффициент загрузки клерка, ρ = λ / μ")
    is_stable: bool
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
    message: str
