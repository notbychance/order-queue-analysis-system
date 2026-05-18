from __future__ import annotations

from typing import Any


class QueueApiError(Exception):
    """Базовая ошибка API-клиента desktop-приложения."""


class QueueApiConnectionError(QueueApiError):
    """Ошибка подключения к FastAPI-серверу."""


class QueueApiResponseError(QueueApiError):
    """Ошибка HTTP-ответа FastAPI-сервера."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        details: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.details = details
