from pydantic import BaseModel, ConfigDict, Field


class QueueAnalysisRequest(BaseModel):
    """Параметры анализа системы массового обслуживания M/M/1."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "lambda_rate": 6.0,
                    "mu_rate": 8.0,
                },
                {
                    "lambda_rate": 8.0,
                    "mu_rate": 8.0,
                },
            ]
        }
    )

    lambda_rate: float = Field(
        ...,
        ge=0,
        description="Интенсивность поступления заказов λ, заказов в день",
        examples=[6.0],
    )
    mu_rate: float = Field(
        ...,
        gt=0,
        description="Интенсивность обслуживания заказов μ, заказов в день",
        examples=[8.0],
    )


class QueueAnalysisResponse(BaseModel):
    """Результат анализа системы массового обслуживания M/M/1."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
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
                {
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
                        "Система неустойчива: интенсивность поступления заказов "
                        "больше или равна интенсивности обслуживания. Очередь "
                        "будет расти неограниченно."
                    ),
                },
            ]
        }
    )

    lambda_rate: float = Field(
        description="Интенсивность поступления заказов λ",
        examples=[6.0],
    )
    mu_rate: float = Field(
        description="Интенсивность обслуживания заказов μ",
        examples=[8.0],
    )

    arrival_rate_unit: str = Field(
        default="заказов/день",
        description="Единица измерения интенсивности поступления",
        examples=["заказов/день"],
    )
    service_rate_unit: str = Field(
        default="заказов/день",
        description="Единица измерения интенсивности обслуживания",
        examples=["заказов/день"],
    )
    time_unit: str = Field(
        default="дней",
        description="Базовая единица измерения времени",
        examples=["дней"],
    )

    is_stable: bool = Field(
        description="Признак устойчивости системы. True, если λ < μ.",
        examples=[True],
    )

    utilization: float = Field(
        description="Коэффициент загрузки клерка ρ = λ / μ",
        examples=[0.75],
    )
    utilization_percent: float = Field(
        description="Коэффициент загрузки клерка в процентах",
        examples=[75.0],
    )

    average_orders_in_system: float | None = Field(
        default=None,
        description="Среднее число заказов в системе L",
        examples=[3.0],
    )
    average_waiting_time: float | None = Field(
        default=None,
        description="Среднее время ожидания начала обработки Wq, дней",
        examples=[0.375],
    )
    average_waiting_time_hours: float | None = Field(
        default=None,
        description="Среднее время ожидания начала обработки Wq, часов",
        examples=[9.0],
    )
    average_time_in_system: float | None = Field(
        default=None,
        description="Среднее время пребывания заказа в системе W, дней",
        examples=[0.5],
    )
    average_time_in_system_hours: float | None = Field(
        default=None,
        description="Среднее время пребывания заказа в системе W, часов",
        examples=[12.0],
    )

    conclusion: str = Field(
        description="Текстовое заключение по результатам анализа",
        examples=[
            "Система устойчива. Клерк загружен на 75.0%. Очередь не растет неограниченно."
        ],
    )


class QueueFormulasResponse(BaseModel):
    """Описание модели M/M/1 и используемых формул."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
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
            ]
        }
    )

    model_name: str = Field(
        description="Название модели массового обслуживания",
        examples=["M/M/1"],
    )
    description: str = Field(
        description="Описание модели",
        examples=[
            "Одноканальная система массового обслуживания с пуассоновским потоком заявок."
        ],
    )
    stability_condition: str = Field(
        description="Условие устойчивости системы",
        examples=["λ < μ"],
    )
    formulas: dict[str, str] = Field(
        description="Список используемых формул",
        examples=[
            {
                "utilization": "ρ = λ / μ",
                "average_orders_in_system": "L = λ / (μ - λ)",
                "average_waiting_time": "Wq = λ / (μ * (μ - λ))",
                "average_time_in_system": "W = 1 / (μ - λ)",
            }
        ],
    )
