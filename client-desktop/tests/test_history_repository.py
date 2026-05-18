from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from app.data.repositories.history_repository import HistoryRepository
from app.data.sqlalchemy_connection_manager import SQLAlchemyConnectionManager
from app.schemas.history import HistoryCreate


def make_history_create(
    index: int = 0,
    *,
    created_at: datetime | None = None,
    is_stable: bool = True,
) -> HistoryCreate:
    if is_stable:
        return HistoryCreate(
            created_at=created_at,
            lambda_rate=6.0 + index,
            mu_rate=10.0 + index,
            is_stable=True,
            utilization=0.6,
            utilization_percent=60.0,
            average_orders_in_system=1.5,
            average_waiting_time=0.15,
            average_waiting_time_hours=3.6,
            average_time_in_system=0.25,
            average_time_in_system_hours=6.0,
            conclusion="Система устойчива.",
        )

    return HistoryCreate(
        created_at=created_at,
        lambda_rate=10.0 + index,
        mu_rate=8.0 + index,
        is_stable=False,
        utilization=1.25,
        utilization_percent=125.0,
        average_orders_in_system=None,
        average_waiting_time=None,
        average_waiting_time_hours=None,
        average_time_in_system=None,
        average_time_in_system_hours=None,
        conclusion="Система неустойчива.",
    )


@pytest.fixture
def repository(tmp_path) -> HistoryRepository:
    manager = SQLAlchemyConnectionManager(tmp_path / "history.sqlite3")
    repo = HistoryRepository(manager, max_items=50)
    repo.initialize_storage()
    return repo


@pytest.mark.unit
@pytest.mark.data
def test_initialize_storage_creates_history_table(tmp_path):
    manager = SQLAlchemyConnectionManager(tmp_path / "history.sqlite3")
    repo = HistoryRepository(manager)

    repo.initialize_storage()

    assert manager.check_connection() is True


@pytest.mark.unit
@pytest.mark.data
def test_add_saves_stable_history_record(repository):
    item = repository.add(make_history_create())

    assert item.id
    assert isinstance(item.created_at, datetime)
    assert item.lambda_rate == 6.0
    assert item.mu_rate == 10.0
    assert item.is_stable is True
    assert item.average_orders_in_system == 1.5
    assert item.conclusion == "Система устойчива."
    assert repository.count() == 1


@pytest.mark.unit
@pytest.mark.data
def test_add_saves_unstable_history_record(repository):
    item = repository.add(make_history_create(is_stable=False))

    assert item.is_stable is False
    assert item.average_orders_in_system is None
    assert item.average_waiting_time is None
    assert item.average_time_in_system is None


@pytest.mark.unit
@pytest.mark.data
def test_list_returns_records_ordered_by_created_at_desc(repository):
    base_time = datetime(2026, 1, 1, tzinfo=timezone.utc)

    first = repository.add(make_history_create(1, created_at=base_time))
    second = repository.add(make_history_create(2, created_at=base_time + timedelta(minutes=1)))
    third = repository.add(make_history_create(3, created_at=base_time + timedelta(minutes=2)))

    items = repository.list()

    assert [item.id for item in items] == [third.id, second.id, first.id]


@pytest.mark.unit
@pytest.mark.data
def test_list_applies_limit(repository):
    base_time = datetime(2026, 1, 1, tzinfo=timezone.utc)

    for index in range(5):
        repository.add(
            make_history_create(
                index,
                created_at=base_time + timedelta(minutes=index),
            )
        )

    items = repository.list(limit=2)

    assert len(items) == 2
    assert items[0].lambda_rate == 10.0
    assert items[1].lambda_rate == 9.0


@pytest.mark.unit
@pytest.mark.data
def test_get_by_id_returns_record(repository):
    item = repository.add(make_history_create())

    found_item = repository.get_by_id(item.id)

    assert found_item is not None
    assert found_item.id == item.id
    assert found_item.lambda_rate == item.lambda_rate


@pytest.mark.unit
@pytest.mark.data
def test_get_by_id_returns_none_for_missing_record(repository):
    assert repository.get_by_id("missing-id") is None


@pytest.mark.unit
@pytest.mark.data
def test_delete_by_id_removes_existing_record(repository):
    item = repository.add(make_history_create())

    deleted = repository.delete_by_id(item.id)

    assert deleted is True
    assert repository.get_by_id(item.id) is None
    assert repository.count() == 0


@pytest.mark.unit
@pytest.mark.data
def test_delete_by_id_returns_false_for_missing_record(repository):
    assert repository.delete_by_id("missing-id") is False


@pytest.mark.unit
@pytest.mark.data
def test_clear_removes_all_records(repository):
    repository.add(make_history_create(1))
    repository.add(make_history_create(2))

    deleted_count = repository.clear()

    assert deleted_count == 2
    assert repository.count() == 0
    assert repository.list() == []


@pytest.mark.unit
@pytest.mark.data
def test_repository_trims_history_to_max_items(tmp_path):
    manager = SQLAlchemyConnectionManager(tmp_path / "history.sqlite3")
    repository = HistoryRepository(manager, max_items=3)
    repository.initialize_storage()

    base_time = datetime(2026, 1, 1, tzinfo=timezone.utc)

    for index in range(5):
        repository.add(
            make_history_create(
                index,
                created_at=base_time + timedelta(minutes=index),
            )
        )

    items = repository.list()

    assert repository.count() == 3
    assert [item.lambda_rate for item in items] == [10.0, 9.0, 8.0]


@pytest.mark.unit
@pytest.mark.data
def test_repository_with_zero_max_items_does_not_keep_history(tmp_path):
    manager = SQLAlchemyConnectionManager(tmp_path / "history.sqlite3")
    repository = HistoryRepository(manager, max_items=0)
    repository.initialize_storage()

    repository.add(make_history_create())

    assert repository.count() == 0
    assert repository.list() == []
