from fastapi import APIRouter

from app.schemas.queue import QueueAnalysisRequest, QueueAnalysisResponse
from app.services.queue_analysis import analyze_queue


router = APIRouter(prefix="/queue", tags=["queue-analysis"])


@router.get("/default")
def get_default_queue_params() -> dict:
    return {
        "lambda_rate": 6,
        "mu_rate": 8,
        "description": "Вариант №17: одноканальная система обслуживания заказов",
    }


@router.post("/analyze", response_model=QueueAnalysisResponse)
def analyze_queue_system(request: QueueAnalysisRequest) -> QueueAnalysisResponse:
    return analyze_queue(request)
