from __future__ import annotations

from app.core.settings import DesktopSettings, get_settings
from app.data.repositories.history_repository import HistoryRepository
from app.data.sqlalchemy_connection_manager import (
    SQLAlchemyConnectionManager,
    create_sqlalchemy_connection_manager,
)
from app.schemas.history import HistoryCreate, HistoryItem


class HistoryService:
    """Сервис локальной истории расчетов desktop-клиента.

    Сервис отделяет UI/ViewModel от конкретной реализации хранения.
    Сейчас используется локальная SQLite-БД через HistoryRepository.
    Сервер FastAPI историю расчетов не хранит.
    """

    def __init__(self, repository: HistoryRepository) -> None:
        self.repository = repository

    def initialize(self) -> None:
        """Создать таблицы локального хранилища, если они еще не созданы."""
        self.repository.initialize_storage()

    def add_history_item(self, data: HistoryCreate) -> HistoryItem:
        """Добавить запись расчета в локальную историю."""
        return self.repository.add(data)

    def get_history(self, limit: int | None = None) -> list[HistoryItem]:
        """Получить локальную историю расчетов от новых записей к старым."""
        return self.repository.list(limit=limit)

    def get_history_item(self, record_id: str) -> HistoryItem | None:
        """Получить одну запись истории по идентификатору."""
        return self.repository.get_by_id(record_id)

    def delete_history_item(self, record_id: str) -> bool:
        """Удалить запись истории по идентификатору."""
        return self.repository.delete_by_id(record_id)

    def clear_history(self) -> int:
        """Очистить локальную историю и вернуть количество удаленных записей."""
        return self.repository.clear()

    def count_history_items(self) -> int:
        """Вернуть количество записей в локальной истории."""
        return self.repository.count()


def create_history_service(
    settings: DesktopSettings | None = None,
    connection_manager: SQLAlchemyConnectionManager | None = None,
) -> HistoryService:
    """Создать сервис истории на основе настроек desktop-клиента."""

    current_settings = settings or get_settings()
    manager = connection_manager or create_sqlalchemy_connection_manager(current_settings)

    repository = HistoryRepository(
        connection_manager=manager,
        max_items=current_settings.max_history_items,
    )

    return HistoryService(repository)
