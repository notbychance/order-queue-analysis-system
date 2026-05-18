from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.queue import router as queue_router
from app.core.config import get_settings


settings = get_settings()


app = FastAPI(
    title=settings.app_name,
    description=(
        "API для анализа одноканальной системы массового обслуживания M/M/1. "
        "Сервер выполняет расчет показателей системы, но не хранит историю расчетов."
    ),
    version="0.1.0",
    debug=settings.debug,
    openapi_tags=[
        {
            "name": "system",
            "description": "Служебные endpoint-ы состояния сервера.",
        },
        {
            "name": "queue-analysis",
            "description": "Анализ системы массового обслуживания M/M/1.",
        },
    ],
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=settings.cors_allow_credentials_effective,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
def health_check() -> dict:
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.app_env,
    }


app.include_router(
    queue_router,
    prefix=settings.api_prefix,
)
