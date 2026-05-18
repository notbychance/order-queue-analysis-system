from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.api.v1.queue import router as queue_router
from app.core.config import get_settings


settings = get_settings()


class HealthCheckResponse(BaseModel):
    status: str = Field(
        description="Текущее состояние сервера",
        examples=["ok"],
    )
    service: str = Field(
        description="Название сервиса",
        examples=["Queue Analysis API"],
    )
    environment: str = Field(
        description="Текущее окружение приложения",
        examples=["development"],
    )


OPENAPI_TAGS = [
    {
        "name": "system",
        "description": "Служебные endpoint-ы для проверки состояния API.",
    },
    {
        "name": "queue-analysis",
        "description": (
            "Endpoint-ы анализа одноканальной системы массового обслуживания "
            "M/M/1: расчет показателей и получение используемых формул."
        ),
    },
]

API_DESCRIPTION = """
API для анализа одноканальной системы массового обслуживания **M/M/1**.

Сервер принимает интенсивность поступления заказов `λ` и интенсивность
обслуживания `μ`, проверяет условие устойчивости `λ < μ` и возвращает
расчетные показатели системы.

Сервер не хранит историю расчетов. История хранится локально на стороне клиентов:

- web-клиент: `localStorage`;
- desktop-клиент: локальная SQLite-БД.
"""


app = FastAPI(
    title=settings.app_name,
    description=API_DESCRIPTION,
    version="0.1.0",
    debug=settings.debug,
    openapi_tags=OPENAPI_TAGS,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    swagger_ui_parameters={
        "defaultModelsExpandDepth": 2,
        "defaultModelExpandDepth": 2,
        "displayRequestDuration": True,
        "filter": True,
        "tryItOutEnabled": True,
    },
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    "/health",
    tags=["system"],
    response_model=HealthCheckResponse,
    summary="Проверить состояние сервера",
    description="Возвращает статус FastAPI-сервера и текущее окружение.",
    responses={
        200: {
            "description": "Сервер доступен.",
            "content": {
                "application/json": {
                    "example": {
                        "status": "ok",
                        "service": "Queue Analysis API",
                        "environment": "development",
                    }
                }
            },
        }
    },
)
def health_check() -> HealthCheckResponse:
    return HealthCheckResponse(
        status="ok",
        service=settings.app_name,
        environment=settings.app_env,
    )


app.include_router(
    queue_router,
    prefix=settings.api_prefix,
)
