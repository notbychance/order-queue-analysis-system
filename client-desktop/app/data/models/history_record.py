from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.data.sqlalchemy_connection_manager import Base


def _generate_history_id() -> str:
    return str(uuid4())


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class HistoryRecord(Base):
    """ORM-модель локальной записи истории расчета desktop-клиента.

    Таблица хранится только в локальной SQLite-БД desktop-приложения.
    Сервер FastAPI историю расчетов не хранит.
    """

    __tablename__ = "history_records"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=_generate_history_id,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utc_now,
        index=True,
    )

    lambda_rate: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    mu_rate: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    is_stable: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        index=True,
    )

    utilization: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    utilization_percent: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    average_orders_in_system: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    average_waiting_time: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    average_waiting_time_hours: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    average_time_in_system: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    average_time_in_system_hours: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    conclusion: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            "HistoryRecord("
            f"id={self.id!r}, "
            f"lambda_rate={self.lambda_rate!r}, "
            f"mu_rate={self.mu_rate!r}, "
            f"is_stable={self.is_stable!r}"
            ")"
        )
