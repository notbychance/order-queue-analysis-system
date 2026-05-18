from __future__ import annotations

from typing import Any

import httpx
from pydantic import ValidationError

from app.api.errors import QueueApiConnectionError, QueueApiResponseError
from app.core.settings import DesktopSettings, get_settings
from app.schemas.queue import (
    QueueAnalysisRequest,
    QueueAnalysisResponse,
    QueueFormulasResponse,
)


class QueueApiClient:
    """HTTP-клиент desktop-приложения для общения с FastAPI-сервером."""

    def __init__(
        self,
        base_url: str,
        timeout_seconds: float = 10.0,
        client: httpx.Client | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self._owns_client = client is None
        self._client = client or httpx.Client(
            base_url=self.base_url,
            timeout=timeout_seconds,
        )

    def __enter__(self) -> QueueApiClient:
        return self

    def __exit__(self, *_exc_info: object) -> None:
        self.close()

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def analyze_queue(
        self,
        request: QueueAnalysisRequest,
    ) -> QueueAnalysisResponse:
        """Выполнить расчет системы массового обслуживания на сервере."""

        response_data = self._request_json(
            method="POST",
            url="/queue/analyze",
            json_data=request.model_dump(),
        )

        try:
            return QueueAnalysisResponse.model_validate(response_data)
        except ValidationError as exc:
            raise QueueApiResponseError(
                "Сервер вернул ответ анализа в неизвестном формате.",
                status_code=200,
                details=exc.errors(),
            ) from exc

    def get_formulas(self) -> QueueFormulasResponse:
        """Получить описание формул модели M/M/1 с FastAPI-сервера."""

        response_data = self._request_json(
            method="GET",
            url="/queue/formulas",
        )

        try:
            return QueueFormulasResponse.model_validate(response_data)
        except ValidationError as exc:
            raise QueueApiResponseError(
                "Сервер вернул описание формул в неизвестном формате.",
                status_code=200,
                details=exc.errors(),
            ) from exc

    def health_check(self) -> dict[str, Any]:
        """Проверить доступность сервера.

        Для health endpoint используется корневой адрес сервера, поэтому при
        API_BASE_URL=http://localhost:8000/api/v1 запрос отправляется на
        http://localhost:8000/health.
        """

        health_url = self._build_health_url()

        try:
            response = httpx.get(health_url, timeout=self.timeout_seconds)
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPStatusError as exc:
            raise QueueApiResponseError(
                "Сервер вернул ошибку при проверке состояния.",
                status_code=exc.response.status_code,
                details=self._safe_json(exc.response),
            ) from exc
        except (httpx.HTTPError, ValueError) as exc:
            raise QueueApiConnectionError(
                "Не удалось проверить доступность FastAPI-сервера."
            ) from exc

        if not isinstance(data, dict):
            raise QueueApiResponseError(
                "Сервер вернул некорректный ответ health check.",
                status_code=200,
                details=data,
            )

        return data

    def _request_json(
        self,
        *,
        method: str,
        url: str,
        json_data: dict[str, Any] | None = None,
    ) -> Any:
        try:
            response = self._client.request(method, url, json=json_data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            raise QueueApiResponseError(
                self._extract_error_message(exc.response),
                status_code=exc.response.status_code,
                details=self._safe_json(exc.response),
            ) from exc
        except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError) as exc:
            raise QueueApiConnectionError(
                "Не удалось подключиться к FastAPI-серверу."
            ) from exc
        except ValueError as exc:
            raise QueueApiResponseError(
                "Сервер вернул ответ не в формате JSON.",
                status_code=200,
            ) from exc

    def _build_health_url(self) -> str:
        if self.base_url.endswith("/api/v1"):
            return self.base_url.removesuffix("/api/v1") + "/health"

        if "/api/" in self.base_url:
            return self.base_url.split("/api/", 1)[0] + "/health"

        return self.base_url + "/health"

    @staticmethod
    def _safe_json(response: httpx.Response) -> Any | None:
        try:
            return response.json()
        except ValueError:
            return None

    @classmethod
    def _extract_error_message(cls, response: httpx.Response) -> str:
        data = cls._safe_json(response)

        if isinstance(data, dict):
            detail = data.get("detail")

            if isinstance(detail, str):
                return detail

            if isinstance(detail, list):
                return "Ошибка валидации данных запроса."

        return f"FastAPI-сервер вернул ошибку HTTP {response.status_code}."


def create_queue_api_client(
    settings: DesktopSettings | None = None,
) -> QueueApiClient:
    current_settings = settings or get_settings()

    return QueueApiClient(
        base_url=current_settings.api_base_url,
        timeout_seconds=current_settings.request_timeout_seconds,
    )
