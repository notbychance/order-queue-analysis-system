from __future__ import annotations

from datetime import datetime, timezone

import pytest

from app.data.repositories.history_repository import HistoryRepository
from app.data.sqlalchemy_connection_manager import SQLAlchemyConnectionManager
from app.schemas.history import HistoryItem


def make_history_item(record_id: str, lambda_rate: float) -> HistoryItem:
    return HistoryItem(
        id=record_id,
        created_at=datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc),
        lambda_rate=lambda_rate,
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
def repository(tmp_path) -> HistoryRepository:
    manager = SQLAlchemyConnectionManager(tmp_path / "history.sqlite3")
    repo = HistoryRepository(manager, max_items=50)
    repo.initialize_storage()
    return repo


@pytest.mark.unit
@pytest.mark.data
def test_import_items_adds_records(repository):
    imported_count = repository.import_items(
        [
            make_history_item("record-1", 6.0),
            make_history_item("record-2", 7.0),
        ]
    )

    assert imported_count == 2
    assert repository.count() == 2
    assert repository.get_by_id("record-1") is not None
    assert repository.get_by_id("record-2") is not None


@pytest.mark.unit
@pytest.mark.data
def test_import_items_skips_duplicates(repository):
    item = make_history_item("record-1", 6.0)

    first_count = repository.import_items([item])
    second_count = repository.import_items([item])

    assert first_count == 1
    assert second_count == 0
    assert repository.count() == 1


@pytest.mark.unit
@pytest.mark.data
def test_import_items_replace_clears_existing_history(repository):
    repository.import_items([make_history_item("old-record", 6.0)])

    imported_count = repository.import_items(
        [make_history_item("new-record", 7.0)],
        replace=True,
    )

    assert imported_count == 1
    assert repository.count() == 1
    assert repository.get_by_id("old-record") is None
    assert repository.get_by_id("new-record") is not None
