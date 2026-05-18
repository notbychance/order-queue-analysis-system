from __future__ import annotations

import sqlite3

import pytest

from app.data.sqlite_connection_manager import SQLiteConnectionManager


@pytest.mark.unit
@pytest.mark.data
def test_check_connection_returns_true(tmp_path):
    manager = SQLiteConnectionManager(tmp_path / "history.sqlite3")

    assert manager.check_connection() is True


@pytest.mark.unit
@pytest.mark.data
def test_connection_manager_creates_database_directory(tmp_path):
    database_path = tmp_path / "nested" / "data" / "history.sqlite3"
    manager = SQLiteConnectionManager(database_path)

    manager.execute("CREATE TABLE example (id INTEGER PRIMARY KEY)")

    assert database_path.exists()


@pytest.mark.unit
@pytest.mark.data
def test_connection_uses_row_factory(tmp_path):
    manager = SQLiteConnectionManager(tmp_path / "history.sqlite3")

    manager.execute_script(
        """
        CREATE TABLE example (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL
        );

        INSERT INTO example (title) VALUES ('first');
        """
    )

    row = manager.fetch_one("SELECT id, title FROM example WHERE id = ?", (1,))

    assert isinstance(row, sqlite3.Row)
    assert row is not None
    assert row["id"] == 1
    assert row["title"] == "first"


@pytest.mark.unit
@pytest.mark.data
def test_connection_commits_successful_transaction(tmp_path):
    manager = SQLiteConnectionManager(tmp_path / "history.sqlite3")

    manager.execute("CREATE TABLE example (id INTEGER PRIMARY KEY, title TEXT NOT NULL)")

    with manager.connection() as connection:
        connection.execute("INSERT INTO example (title) VALUES (?)", ("committed",))

    rows = manager.fetch_all("SELECT title FROM example")

    assert [row["title"] for row in rows] == ["committed"]


@pytest.mark.unit
@pytest.mark.data
def test_connection_rolls_back_failed_transaction(tmp_path):
    manager = SQLiteConnectionManager(tmp_path / "history.sqlite3")

    manager.execute("CREATE TABLE example (id INTEGER PRIMARY KEY, title TEXT NOT NULL)")

    with pytest.raises(RuntimeError):
        with manager.connection() as connection:
            connection.execute("INSERT INTO example (title) VALUES (?)", ("rollback",))
            raise RuntimeError("transaction failed")

    rows = manager.fetch_all("SELECT title FROM example")

    assert rows == []


@pytest.mark.unit
@pytest.mark.data
def test_get_sqlite_version_returns_string(tmp_path):
    manager = SQLiteConnectionManager(tmp_path / "history.sqlite3")

    version = manager.get_sqlite_version()

    assert isinstance(version, str)
    assert version != ""
