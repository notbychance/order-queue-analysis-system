from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import Engine, event, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy import create_engine

from app.core.settings import DesktopSettings, get_settings


class Base(DeclarativeBase):
    """Базовый класс для всех SQLAlchemy ORM-моделей desktop-клиента."""


class SQLAlchemyConnectionManager:
    """Менеджер подключения к локальной SQLite-БД через SQLAlchemy.

    Эта БД используется только desktop-клиентом для локальной истории расчетов.
    Сервер FastAPI остается stateless и не хранит глобальную историю.
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

        self._engine: Engine | None = None
        self._session_factory: sessionmaker[Session] | None = None

    @property
    def is_memory_database(self) -> bool:
        return str(self.database_path) == ":memory:"

    @property
    def database_url(self) -> URL:
        if self.is_memory_database:
            return URL.create("sqlite+pysqlite", database=":memory:")

        return URL.create(
            "sqlite+pysqlite",
            database=str(self.database_path.resolve()),
        )

    def ensure_database_directory(self) -> None:
        if self.is_memory_database:
            return

        self.database_path.parent.mkdir(parents=True, exist_ok=True)

    def create_engine(self) -> Engine:
        self.ensure_database_directory()

        engine = create_engine(
            self.database_url,
            echo=self.echo_sql,
            future=True,
            connect_args={
                "timeout": self.timeout_seconds,
                "check_same_thread": False,
            },
        )

        self._configure_engine(engine)

        return engine

    def _configure_engine(self, engine: Engine) -> None:
        timeout_ms = int(self.timeout_seconds * 1000)
        is_memory_database = self.is_memory_database

        @event.listens_for(engine, "connect")
        def configure_sqlite_connection(dbapi_connection, _connection_record) -> None:
            cursor = dbapi_connection.cursor()

            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute(f"PRAGMA busy_timeout = {timeout_ms}")

            if not is_memory_database:
                cursor.execute("PRAGMA journal_mode = WAL")

            cursor.close()

    @property
    def engine(self) -> Engine:
        if self._engine is None:
            self._engine = self.create_engine()

        return self._engine

    @property
    def session_factory(self) -> sessionmaker[Session]:
        if self._session_factory is None:
            self._session_factory = sessionmaker(
                bind=self.engine,
                autoflush=False,
                autocommit=False,
                expire_on_commit=False,
                future=True,
            )

        return self._session_factory

    @contextmanager
    def session(self) -> Iterator[Session]:
        session = self.session_factory()

        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def init_database(self) -> None:
        Base.metadata.create_all(self.engine)

    def drop_database(self) -> None:
        Base.metadata.drop_all(self.engine)

    def check_connection(self) -> bool:
        with self.session() as session:
            result = session.execute(text("SELECT 1 AS result")).scalar_one()

        return result == 1

    def get_sqlite_version(self) -> str:
        with self.session() as session:
            version = session.execute(text("SELECT sqlite_version()")).scalar_one()

        return str(version)

    def dispose(self) -> None:
        if self._engine is not None:
            self._engine.dispose()

        self._engine = None
        self._session_factory = None


def create_sqlalchemy_connection_manager(
    settings: DesktopSettings | None = None,
) -> SQLAlchemyConnectionManager:
    current_settings = settings or get_settings()

    return SQLAlchemyConnectionManager(
        database_path=current_settings.sqlite_database_path,
        timeout_seconds=current_settings.sqlite_connection_timeout_seconds,
        echo_sql=current_settings.sqlite_echo_sql,
    )
