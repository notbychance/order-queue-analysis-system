from __future__ import annotations

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.data.models.history_record import HistoryRecord
from app.data.sqlalchemy_connection_manager import SQLAlchemyConnectionManager
from app.schemas.history import HistoryCreate, HistoryItem


class HistoryRepository:
    """Репозиторий локальной истории расчетов desktop-клиента.

    Репозиторий работает только с локальной SQLite-БД через SQLAlchemy.
    Сервер FastAPI историю расчетов не хранит.
    """

    def __init__(
        self,
        connection_manager: SQLAlchemyConnectionManager,
        max_items: int = 50,
    ) -> None:
        self.connection_manager = connection_manager
        self.max_items = max_items

    def initialize_storage(self) -> None:
        self.connection_manager.init_database()

    def add(self, data: HistoryCreate) -> HistoryItem:
        with self.connection_manager.session() as session:
            record = self._create_record(data)

            session.add(record)
            session.flush()

            # Сохраняем DTO до обрезки истории. Это важно для max_items=0:
            # запись получает id/created_at, но сразу удаляется из хранилища.
            created_item = self._to_schema(record)

            self._trim_history(session)

            return created_item

    def import_items(
        self,
        items: list[HistoryItem],
        *,
        replace: bool = False,
    ) -> int:
        """Импортировать записи истории.

        При append-импорте дубликаты по id пропускаются.
        При replace-импорте текущая история очищается перед добавлением записей.
        """

        imported_count = 0

        with self.connection_manager.session() as session:
            if replace:
                session.execute(delete(HistoryRecord))

            for item in items:
                if not replace and session.get(HistoryRecord, item.id) is not None:
                    continue

                record = self._create_record_from_item(item)
                session.add(record)
                imported_count += 1

            session.flush()
            self._trim_history(session)

        return imported_count

    def list(self, limit: int | None = None) -> list[HistoryItem]:
        safe_limit = self._normalize_limit(limit)

        query = (
            select(HistoryRecord)
            .order_by(HistoryRecord.created_at.desc(), HistoryRecord.id.desc())
            .limit(safe_limit)
        )

        with self.connection_manager.session() as session:
            records = session.scalars(query).all()

        return [self._to_schema(record) for record in records]

    def get_by_id(self, record_id: str) -> HistoryItem | None:
        query = select(HistoryRecord).where(HistoryRecord.id == record_id)

        with self.connection_manager.session() as session:
            record = session.scalars(query).first()

        if record is None:
            return None

        return self._to_schema(record)

    def delete_by_id(self, record_id: str) -> bool:
        query = delete(HistoryRecord).where(HistoryRecord.id == record_id)

        with self.connection_manager.session() as session:
            result = session.execute(query)

        return result.rowcount > 0

    def clear(self) -> int:
        with self.connection_manager.session() as session:
            deleted_count = self._count_records(session)
            session.execute(delete(HistoryRecord))

        return deleted_count

    def count(self) -> int:
        with self.connection_manager.session() as session:
            return self._count_records(session)

    def _create_record(self, data: HistoryCreate) -> HistoryRecord:
        values = data.model_dump(exclude_none=True)
        return HistoryRecord(**values)

    @staticmethod
    def _create_record_from_item(item: HistoryItem) -> HistoryRecord:
        values = item.model_dump()
        return HistoryRecord(**values)

    def _trim_history(self, session: Session) -> None:
        if self.max_items <= 0:
            session.execute(delete(HistoryRecord))
            return

        ids_to_delete = session.scalars(
            select(HistoryRecord.id)
            .order_by(HistoryRecord.created_at.desc(), HistoryRecord.id.desc())
            .offset(self.max_items)
        ).all()

        if not ids_to_delete:
            return

        session.execute(
            delete(HistoryRecord).where(HistoryRecord.id.in_(ids_to_delete))
        )

    def _normalize_limit(self, limit: int | None) -> int:
        if limit is None:
            return self.max_items

        if limit <= 0:
            return self.max_items

        return min(limit, self.max_items)

    @staticmethod
    def _count_records(session: Session) -> int:
        return int(session.scalar(select(func.count()).select_from(HistoryRecord)) or 0)

    @staticmethod
    def _to_schema(record: HistoryRecord) -> HistoryItem:
        return HistoryItem.model_validate(record)
