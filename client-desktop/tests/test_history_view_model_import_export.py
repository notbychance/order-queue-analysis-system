from __future__ import annotations

from datetime import datetime, timezone

import pytest

from app.schemas.history import HistoryItem
from app.viewmodels.history_view_model import HistoryViewModel


def make_history_item(record_id: str = "record-1") -> HistoryItem:
    return HistoryItem(
        id=record_id,
        created_at=datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc),
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


class FakeHistoryService:
    def __init__(self) -> None:
        self.items = [make_history_item()]
        self.exported_path = None
        self.imported_path = None

    def get_history(self, limit: int | None = None):
        return self.items

    def get_history_item(self, record_id: str):
        return self.items[0] if record_id == "record-1" else None

    def delete_history_item(self, record_id: str) -> bool:
        return True

    def clear_history(self) -> int:
        self.items = []
        return 1

    def count_history_items(self) -> int:
        return len(self.items)

    def export_history_to_file(self, file_path):
        self.exported_path = file_path
        return file_path

    def import_history_from_file(self, file_path, *, replace: bool = False) -> int:
        self.imported_path = file_path
        return 1


@pytest.mark.unit
@pytest.mark.ui
def test_export_history_converts_qml_file_url_to_path(tmp_path):
    service = FakeHistoryService()
    view_model = HistoryViewModel(service)

    export_file = tmp_path / "history.json"
    view_model.exportHistory(export_file.as_uri())

    assert service.exported_path == export_file
    assert "экспортирована" in view_model.statusMessage.lower()


@pytest.mark.unit
@pytest.mark.ui
def test_import_history_converts_qml_file_url_to_path(tmp_path):
    service = FakeHistoryService()
    view_model = HistoryViewModel(service)

    import_file = tmp_path / "history.json"
    import_file.write_text("{}", encoding="utf-8")

    view_model.importHistory(import_file.as_uri())

    assert service.imported_path == import_file
    assert "Импортировано записей: 1" in view_model.statusMessage
