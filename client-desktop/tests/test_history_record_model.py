from __future__ import annotations

from datetime import datetime

import pytest

from app.data.models.history_record import HistoryRecord
from app.data.sqlalchemy_connection_manager import Base, SQLAlchemyConnectionManager


@pytest.mark.unit
@pytest.mark.data
def test_history_record_table_is_created(tmp_path):
    manager = SQLAlchemyConnectionManager(tmp_path / "history.sqlite3")

    Base.metadata.create_all(manager.engine)

    table_names = Base.metadata.tables.keys()

    assert "history_records" in table_names


@pytest.mark.unit
@pytest.mark.data
def test_history_record_can_be_saved_and_loaded(tmp_path):
    manager = SQLAlchemyConnectionManager(tmp_path / "history.sqlite3")
    Base.metadata.create_all(manager.engine)

    with manager.session() as session:
        record = HistoryRecord(
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
        session.add(record)

    with manager.session() as session:
        saved_record = session.query(HistoryRecord).one()

    assert saved_record.id
    assert isinstance(saved_record.created_at, datetime)
    assert saved_record.lambda_rate == 6.0
    assert saved_record.mu_rate == 8.0
    assert saved_record.is_stable is True
    assert saved_record.utilization == 0.75
    assert saved_record.utilization_percent == 75.0
    assert saved_record.average_orders_in_system == 3.0
    assert saved_record.average_waiting_time == 0.375
    assert saved_record.average_waiting_time_hours == 9.0
    assert saved_record.average_time_in_system == 0.5
    assert saved_record.average_time_in_system_hours == 12.0
    assert saved_record.conclusion == "Система устойчива."


@pytest.mark.unit
@pytest.mark.data
def test_history_record_supports_unstable_result_with_empty_metrics(tmp_path):
    manager = SQLAlchemyConnectionManager(tmp_path / "history.sqlite3")
    Base.metadata.create_all(manager.engine)

    with manager.session() as session:
        record = HistoryRecord(
            lambda_rate=10.0,
            mu_rate=8.0,
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
        session.add(record)

    with manager.session() as session:
        saved_record = session.query(HistoryRecord).one()

    assert saved_record.is_stable is False
    assert saved_record.average_orders_in_system is None
    assert saved_record.average_waiting_time is None
    assert saved_record.average_waiting_time_hours is None
    assert saved_record.average_time_in_system is None
    assert saved_record.average_time_in_system_hours is None


@pytest.mark.unit
@pytest.mark.data
def test_history_record_repr_contains_key_fields():
    record = HistoryRecord(
        id="test-id",
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

    representation = repr(record)

    assert "HistoryRecord" in representation
    assert "test-id" in representation
    assert "lambda_rate=6.0" in representation
    assert "mu_rate=8.0" in representation
    assert "is_stable=True" in representation
