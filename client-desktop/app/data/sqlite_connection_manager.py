from __future__ import annotations

import logging
import sqlite3
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from app.core.settings import DesktopSettings, get_settings


logger = logging.getLogger(__name__)


class SQLiteConnectionManager:
    """Менеджер подключений к локальной SQLite-базе desktop-клиента.

    Сервер FastAPI не использует эту базу. Она нужна только desktop-клиенту
    для локального хранения истории расчетов.
    """

    def __init__(
        self,
        database_path: str | Path,
        timeout_seconds: float = 5.0,
        echo_sql: bool = False,
    ) -> None:
        self.database_path = Path(database_path).expanduser()
        self.timeout_seconds = timeout_seconds
        self.echo_sql = echo_sql

    @property
    def is_memory_database(self) -> bool:
        return str(self.database_path) == ":memory:"

    def ensure_database_directory(self) -> None:
        if self.is_memory_database:
            return

        self.database_path.parent.mkdir(parents=True, exist_ok=True)

    def create_connection(self) -> sqlite3.Connection:
        self.ensure_database_directory()

        connection = sqlite3.connect(
            str(self.database_path),
            timeout=self.timeout_seconds,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
        )
        connection.row_factory = sqlite3.Row

        if self.echo_sql:
            connection.set_trace_callback(logger.debug)

        self._configure_connection(connection)

        return connection

    def _configure_connection(self, connection: sqlite3.Connection) -> None:
        timeout_ms = int(self.timeout_seconds * 1000)

        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute(f"PRAGMA busy_timeout = {timeout_ms}")

        if not self.is_memory_database:
            connection.execute("PRAGMA journal_mode = WAL")

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        connection = self.create_connection()

        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def execute(
        self,
        query: str,
        params: Sequence[Any] | None = None,
    ) -> None:
        with self.connection() as connection:
            connection.execute(query, params or ())

    def execute_script(self, script: str) -> None:
        with self.connection() as connection:
            connection.executescript(script)

    def fetch_one(
        self,
        query: str,
        params: Sequence[Any] | None = None,
    ) -> sqlite3.Row | None:
        with self.connection() as connection:
            cursor = connection.execute(query, params or ())
            return cursor.fetchone()

    def fetch_all(
        self,
        query: str,
        params: Sequence[Any] | None = None,
    ) -> list[sqlite3.Row]:
        with self.connection() as connection:
            cursor = connection.execute(query, params or ())
            return list(cursor.fetchall())

    def check_connection(self) -> bool:
        row = self.fetch_one("SELECT 1 AS result")
        return row is not None and row["result"] == 1

    def get_sqlite_version(self) -> str:
        row = self.fetch_one("SELECT sqlite_version() AS version")

        if row is None:
            return "unknown"

        return str(row["version"])


def create_sqlite_connection_manager(
    settings: DesktopSettings | None = None,
) -> SQLiteConnectionManager:
    current_settings = settings or get_settings()

    return SQLiteConnectionManager(
        database_path=current_settings.sqlite_database_path,
        timeout_seconds=current_settings.sqlite_connection_timeout_seconds,
        echo_sql=current_settings.sqlite_echo_sql,
    )
