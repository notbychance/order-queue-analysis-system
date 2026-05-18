from __future__ import annotations

from datetime import datetime, timezone

import pytest

from app.schemas.history import HistoryItem
from app.viewmodels.history_view_model import HistoryViewModel


def make_history_item(
    record_id: str = "record-1",
    *,
    is_stable: bool = True,
) -> HistoryItem:
    return HistoryItem(
        id=record_id,
        created_at=datetime(2026, 1, 1, 12, 30, tzinfo=timezone.utc),
        lambda_rate=6.0,
        mu_rate=8.0,
        is_stable=is_stable,
        utilization=0.75,
        utilization_percent=75.0,
        average_orders_in_system=3.0 if is_stable else None,
        average_waiting_time=0.375 if is_stable else None,
        average_waiting_time_hours=9.0 if is_stable else None,
        average_time_in_system=0.5 if is_stable else None,
        average_time_in_system_hours=12.0 if is_stable else None,
        conclusion="Система устойчива." if is_stable else "Система неустойчива.",
    )


class FakeHistoryService:
    def __init__(self, items: list[HistoryItem] | None = None) -> None:
        self.items = items or []
        self.deleted_ids: list[str] = []
        self.clear_called = False

    def get_history(self, limit: int | None = None) -> list[HistoryItem]:
        if limit is None:
            return list(self.items)

        return self.items[:limit]

    def get_history_item(self, record_id: str) -> HistoryItem | None:
        return next((item for item in self.items if item.id == record_id), None)

    def delete_history_item(self, record_id: str) -> bool:
        found = self.get_history_item(record_id)

        if found is None:
            return False

        self.deleted_ids.append(record_id)
        self.items = [item for item in self.items if item.id != record_id]
        return True

    def clear_history(self) -> int:
        deleted_count = len(self.items)
        self.items = []
        self.clear_called = True
        return deleted_count

    def count_history_items(self) -> int:
        return len(self.items)


@pytest.mark.unit
@pytest.mark.ui
def test_load_history_fills_qml_items():
    service = FakeHistoryService([make_history_item()])
    view_model = HistoryViewModel(service)

    view_model.loadHistory()

    assert view_model.hasHistory is True
    assert view_model.historyCount == 1

    qml_item = view_model.historyItems[0]
    assert qml_item["id"] == "record-1"
    assert qml_item["createdAt"] == "01.01.2026 12:30"
    assert qml_item["lambdaRate"] == "6"
    assert qml_item["muRate"] == "8"
    assert qml_item["stabilityText"] == "Устойчива"
    assert qml_item["utilizationPercent"] == "75 %"
    assert qml_item["averageOrders"] == "3"
    assert qml_item["averageWaitingTimeHours"] == "9 ч"
    assert qml_item["averageTimeInSystemHours"] == "12 ч"


@pytest.mark.unit
@pytest.mark.ui
def test_load_history_formats_unstable_item():
    service = FakeHistoryService([make_history_item(is_stable=False)])
    view_model = HistoryViewModel(service)

    view_model.loadHistory()

    qml_item = view_model.historyItems[0]

    assert qml_item["stabilityText"] == "Неустойчива"
    assert qml_item["averageOrders"] == "—"
    assert qml_item["averageWaitingTimeHours"] == "—"
    assert qml_item["averageTimeInSystemHours"] == "—"


@pytest.mark.unit
@pytest.mark.ui
def test_delete_history_item_removes_item_and_reloads_history():
    service = FakeHistoryService([make_history_item()])
    view_model = HistoryViewModel(service)

    view_model.loadHistory()
    view_model.deleteHistoryItem("record-1")

    assert service.deleted_ids == ["record-1"]
    assert view_model.hasHistory is False
    assert view_model.historyItems == []


@pytest.mark.unit
@pytest.mark.ui
def test_delete_history_item_sets_error_for_missing_record():
    service = FakeHistoryService([])
    view_model = HistoryViewModel(service)

    view_model.deleteHistoryItem("missing-id")

    assert "не найдена" in view_model.errorMessage


@pytest.mark.unit
@pytest.mark.ui
def test_clear_history_removes_all_items():
    service = FakeHistoryService([make_history_item()])
    view_model = HistoryViewModel(service)

    view_model.loadHistory()
    view_model.clearHistory()

    assert service.clear_called is True
    assert view_model.hasHistory is False
    assert view_model.historyItems == []


@pytest.mark.unit
@pytest.mark.ui
def test_repeat_history_item_emits_requested_values(qtbot):
    service = FakeHistoryService([make_history_item()])
    view_model = HistoryViewModel(service)

    with qtbot.waitSignal(view_model.repeatRequested, timeout=1000) as blocker:
        view_model.repeatHistoryItem("record-1")

    assert blocker.args == ["6", "8"]


@pytest.mark.unit
@pytest.mark.ui
def test_repeat_history_item_sets_error_for_missing_record():
    service = FakeHistoryService([])
    view_model = HistoryViewModel(service)

    view_model.repeatHistoryItem("missing-id")

    assert "не найдена" in view_model.errorMessage
