from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from app.schemas.history import HistoryItem


HISTORY_EXPORT_VERSION = 1


class HistoryFileError(Exception):
    """Ошибка импорта или экспорта локальной истории."""


def export_history_items_to_json(
    file_path: str | Path,
    items: list[HistoryItem],
) -> Path:
    path = Path(file_path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "version": HISTORY_EXPORT_VERSION,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "items": [
            item.model_dump(mode="json")
            for item in items
        ],
    }

    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return path


def import_history_items_from_json(
    file_path: str | Path,
) -> list[HistoryItem]:
    path = Path(file_path).expanduser()

    if not path.exists():
        raise HistoryFileError("Файл истории не найден.")

    if path.suffix.lower() != ".json":
        raise HistoryFileError("История должна импортироваться из JSON-файла.")

    try:
        raw_data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise HistoryFileError("Файл истории содержит некорректный JSON.") from exc

    raw_items = _extract_raw_items(raw_data)

    try:
        return [
            HistoryItem.model_validate(item)
            for item in raw_items
        ]
    except ValidationError as exc:
        raise HistoryFileError("Структура файла истории не соответствует ожидаемой.") from exc


def _extract_raw_items(raw_data: Any) -> list[Any]:
    if isinstance(raw_data, list):
        return raw_data

    if isinstance(raw_data, dict):
        raw_items = raw_data.get("items")

        if isinstance(raw_items, list):
            return raw_items

    raise HistoryFileError("Файл истории должен содержать массив записей items.")
