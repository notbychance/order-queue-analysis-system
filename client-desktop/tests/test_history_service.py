from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest

from app.core.settings import get_settings
from app.data.sqlalchemy_connection_manager import SQLAlchemyConnectionManager
from app.schemas.history import HistoryCreate
from app.services.history_service import HistoryService, create_history_service


def make_history_create(
    index: int = 0,
    *,
    created_at: datetime | None = None,
    is_stable: bool = True,
) -> HistoryCreate:
    if is_stable:
        return HistoryCreate(
            created_at=created_at,
            lambda_rate=5.0 + index,
            mu_rate=10.0 + index,
            is_stable=True,
            utilization=0.5,
            utilization_percent=50.0,
            average_orders_in_system=1.0,
            average_waiting_time=0.1,
            average_waiting_time_hours=2.4,
            average_time_in_system=0.2,
            average_time_in_system_hours=4.8,
            conclusion="Система устойчива.",
        )

    return HistoryCreate(
        created_at=created_at,
        lambda_rate=12.0 + index,
        mu_rate=10.0 + index,
        is_stable=False,
        utilization=1.2,
        utilization_percent=120.0,
        average_orders_in_system=None,
        average_waiting_time=None,
        average_waiting_time_hours=None,
        average_time_in_system=None,
        average_time_in_system_hours=None,
        conclusion="Система неустойчива.",
    )


@pytest.fixture
def history_service(tmp_path) -> HistoryService:
    settings = replace(
        get_settings(),
        sqlite_database_path=tmp_path / "history.sqlite3",
        max_history_items=50,
    )
    service = create_history_service(settings=settings)
    service.initialize()
    return service


@pytest.mark.unit
@pytest.mark.data
def test_create_history_service_builds_service_from_settings(tmp_path):
    settings = replace(
        get_settings(),
        sqlite_database_path=tmp_path / "history.sqlite3",
        max_history_items=10,
    )

    service = create_history_service(settings=settings)
    service.initialize()

    assert service.count_history_items() == 0


@pytest.mark.unit
@pytest.mark.data
def test_create_history_service_accepts_existing_connection_manager(tmp_path):
    settings = replace(
        get_settings(),
        sqlite_database_path=tmp_path / "unused.sqlite3",
        max_history_items=10,
    )
    manager = SQLAlchemyConnectionManager(tmp_path / "custom.sqlite3")

    service = create_history_service(
        settings=settings,
        connection_manager=manager,
    )
    service.initialize()

    service.add_history_item(make_history_create())

    assert service.count_history_items() == 1
    assert (tmp_path / "custom.sqlite3").exists()


@pytest.mark.unit
@pytest.mark.data
def test_add_history_item_saves_record(history_service):
    item = history_service.add_history_item(make_history_create())

    assert item.id
    assert item.lambda_rate == 5.0
    assert item.mu_rate == 10.0
    assert item.is_stable is True
    assert history_service.count_history_items() == 1


@pytest.mark.unit
@pytest.mark.data
def test_get_history_returns_records_from_newest_to_oldest(history_service):
    base_time = datetime(2026, 1, 1, tzinfo=timezone.utc)

    first = history_service.add_history_item(
        make_history_create(1, created_at=base_time)
    )
    second = history_service.add_history_item(
        make_history_create(2, created_at=base_time + timedelta(minutes=1))
    )

    history = history_service.get_history()

    assert [item.id for item in history] == [second.id, first.id]


@pytest.mark.unit
@pytest.mark.data
def test_get_history_respects_limit(history_service):
    base_time = datetime(2026, 1, 1, tzinfo=timezone.utc)

    for index in range(5):
        history_service.add_history_item(
            make_history_create(
                index,
                created_at=base_time + timedelta(minutes=index),
            )
        )

    history = history_service.get_history(limit=2)

    assert len(history) == 2


@pytest.mark.unit
@pytest.mark.data
def test_get_history_item_returns_record(history_service):
    item = history_service.add_history_item(make_history_create())

    found_item = history_service.get_history_item(item.id)

    assert found_item is not None
    assert found_item.id == item.id


@pytest.mark.unit
@pytest.mark.data
def test_get_history_item_returns_none_for_missing_record(history_service):
    assert history_service.get_history_item("missing-id") is None


@pytest.mark.unit
@pytest.mark.data
def test_delete_history_item_removes_record(history_service):
    item = history_service.add_history_item(make_history_create())

    deleted = history_service.delete_history_item(item.id)

    assert deleted is True
    assert history_service.get_history_item(item.id) is None
    assert history_service.count_history_items() == 0


@pytest.mark.unit
@pytest.mark.data
def test_clear_history_removes_all_records(history_service):
    history_service.add_history_item(make_history_create(1))
    history_service.add_history_item(make_history_create(2, is_stable=False))

    deleted_count = history_service.clear_history()

    assert deleted_count == 2
    assert history_service.count_history_items() == 0
    assert history_service.get_history() == []
