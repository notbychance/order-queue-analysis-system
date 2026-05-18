from __future__ import annotations

import pytest
from sqlalchemy import String, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.data.sqlalchemy_connection_manager import SQLAlchemyConnectionManager


class SqlAlchemyTestBase(DeclarativeBase):
    pass


class ExampleRecord(SqlAlchemyTestBase):
    __tablename__ = "example_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)


@pytest.mark.unit
@pytest.mark.data
def test_check_connection_returns_true(tmp_path):
    manager = SQLAlchemyConnectionManager(tmp_path / "history.sqlite3")

    assert manager.check_connection() is True


@pytest.mark.unit
@pytest.mark.data
def test_connection_manager_creates_database_directory(tmp_path):
    database_path = tmp_path / "nested" / "data" / "history.sqlite3"
    manager = SQLAlchemyConnectionManager(database_path)

    SqlAlchemyTestBase.metadata.create_all(manager.engine)

    assert database_path.exists()


@pytest.mark.unit
@pytest.mark.data
def test_session_commits_successful_transaction(tmp_path):
    manager = SQLAlchemyConnectionManager(tmp_path / "history.sqlite3")
    SqlAlchemyTestBase.metadata.create_all(manager.engine)

    with manager.session() as session:
        session.add(ExampleRecord(title="committed"))

    with manager.session() as session:
        records = session.query(ExampleRecord).all()

    assert len(records) == 1
    assert records[0].title == "committed"


@pytest.mark.unit
@pytest.mark.data
def test_session_rolls_back_failed_transaction(tmp_path):
    manager = SQLAlchemyConnectionManager(tmp_path / "history.sqlite3")
    SqlAlchemyTestBase.metadata.create_all(manager.engine)

    with pytest.raises(RuntimeError):
        with manager.session() as session:
            session.add(ExampleRecord(title="rollback"))
            raise RuntimeError("transaction failed")

    with manager.session() as session:
        records = session.query(ExampleRecord).all()

    assert records == []


@pytest.mark.unit
@pytest.mark.data
def test_foreign_keys_are_enabled(tmp_path):
    manager = SQLAlchemyConnectionManager(tmp_path / "history.sqlite3")

    with manager.session() as session:
        foreign_keys_enabled = session.execute(text("PRAGMA foreign_keys")).scalar_one()

    assert foreign_keys_enabled == 1


@pytest.mark.unit
@pytest.mark.data
def test_get_sqlite_version_returns_string(tmp_path):
    manager = SQLAlchemyConnectionManager(tmp_path / "history.sqlite3")

    version = manager.get_sqlite_version()

    assert isinstance(version, str)
    assert version != ""


@pytest.mark.unit
@pytest.mark.data
def test_dispose_resets_engine_and_session_factory(tmp_path):
    manager = SQLAlchemyConnectionManager(tmp_path / "history.sqlite3")

    first_engine = manager.engine
    _ = manager.session_factory

    manager.dispose()

    assert manager.engine is not first_engine