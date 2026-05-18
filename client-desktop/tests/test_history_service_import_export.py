from __future__ import annotations

from datetime import datetime, timezone

import pytest

from app.data.repositories.history_repository import HistoryRepository
from app.data.sqlalchemy_connection_manager import SQLAlchemyConnectionManager
from app.schemas.history import HistoryItem
from app.services.history_service import HistoryService


def make_history_item(record_id: str = "record-1") -> HistoryItem:
    return HistoryItem(
        id=record_id,
        created_at=datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc),
        lambda_rate=6.0,
        mu_rate=8.0,
        is_stable=True,
        utilization=0.75,
        utilization_percent=75.0,
        average_orders_in_system=3.0,
        average_waiting_time=0.375,
        average_waiting_time_hours=9.0,
        average_time_in_system=0.5,
        average_time_in_system_hours=12.0,
        conclusion="Система устойчива.",
    )


@pytest.fixture
def service(tmp_path) -> HistoryService:
    manager = SQLAlchemyConnectionManager(tmp_path / "history.sqlite3")
    repository = HistoryRepository(manager, max_items=50)
    service = HistoryService(repository)
    service.initialize()
    return service


@pytest.mark.unit
@pytest.mark.data
def test_export_and_import_history_file(service, tmp_path):
    service.import_history_items([make_history_item("record-1")])

    export_path = tmp_path / "history.json"
    service.export_history_to_file(export_path)

    service.clear_history()
    assert service.count_history_items() == 0

    imported_count = service.import_history_from_file(export_path)

    assert imported_count == 1
    assert service.count_history_items() == 1
    assert service.get_history_item("record-1") is not None


@pytest.mark.unit
@pytest.mark.data
def test_import_history_items_delegates_to_repository(service):
    imported_count = service.import_history_items([make_history_item("record-1")])

    assert imported_count == 1
    assert service.count_history_items() == 1
