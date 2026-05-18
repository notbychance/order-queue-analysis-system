from __future__ import annotations

from datetime import datetime, timezone

import pytest

from app.schemas.history import HistoryItem
from app.services.history_file_service import (
    HistoryFileError,
    export_history_items_to_json,
    import_history_items_from_json,
)


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


@pytest.mark.unit
@pytest.mark.data
def test_export_and_import_history_items(tmp_path):
    file_path = tmp_path / "history.json"
    item = make_history_item()

    export_history_items_to_json(file_path, [item])
    imported_items = import_history_items_from_json(file_path)

    assert len(imported_items) == 1
    assert imported_items[0].id == item.id
    assert imported_items[0].lambda_rate == 6.0
    assert imported_items[0].created_at.year == 2026


@pytest.mark.unit
@pytest.mark.data
def test_import_accepts_raw_array_format(tmp_path):
    file_path = tmp_path / "history.json"
    item = make_history_item()

    file_path.write_text(
        item.model_dump_json(),
        encoding="utf-8",
    )

    with pytest.raises(HistoryFileError):
        import_history_items_from_json(file_path)

    file_path.write_text(
        "[" + item.model_dump_json() + "]",
        encoding="utf-8",
    )

    imported_items = import_history_items_from_json(file_path)

    assert len(imported_items) == 1
    assert imported_items[0].id == "record-1"


@pytest.mark.unit
@pytest.mark.data
def test_import_rejects_missing_file(tmp_path):
    with pytest.raises(HistoryFileError, match="не найден"):
        import_history_items_from_json(tmp_path / "missing.json")


@pytest.mark.unit
@pytest.mark.data
def test_import_rejects_non_json_file(tmp_path):
    file_path = tmp_path / "history.txt"
    file_path.write_text("[]", encoding="utf-8")

    with pytest.raises(HistoryFileError, match="JSON"):
        import_history_items_from_json(file_path)


@pytest.mark.unit
@pytest.mark.data
def test_import_rejects_invalid_json(tmp_path):
    file_path = tmp_path / "history.json"
    file_path.write_text("{", encoding="utf-8")

    with pytest.raises(HistoryFileError, match="некорректный JSON"):
        import_history_items_from_json(file_path)


@pytest.mark.unit
@pytest.mark.data
def test_import_rejects_invalid_structure(tmp_path):
    file_path = tmp_path / "history.json"
    file_path.write_text('{"items": [{"id": "broken"}]}', encoding="utf-8")

    with pytest.raises(HistoryFileError, match="не соответствует"):
        import_history_items_from_json(file_path)
