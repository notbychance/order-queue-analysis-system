from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


CLIENT_DESKTOP_DIR = Path(__file__).resolve().parents[2]
DEFAULT_ENV_FILE = CLIENT_DESKTOP_DIR / ".env"


def _read_env_file(env_file: Path) -> dict[str, str]:
    if not env_file.exists():
        return {}

    values: dict[str, str] = {}

    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")

    return values


def _get_env_value(
    file_values: dict[str, str],
    key: str,
    default: str,
) -> str:
    return os.getenv(key, file_values.get(key, default))


def _parse_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _parse_int(value: str, default: int) -> int:
    try:
        return int(value)
    except ValueError:
        return default


def _parse_float(value: str, default: float) -> float:
    try:
        return float(value)
    except ValueError:
        return default


def _resolve_project_path(path_value: str) -> Path:
    path = Path(path_value).expanduser()

    if path.is_absolute():
        return path

    return CLIENT_DESKTOP_DIR / path


@dataclass(frozen=True)
class DesktopSettings:
    app_name: str
    app_env: str
    log_level: str

    api_base_url: str
    request_timeout_seconds: float

    history_storage_type: str
    history_json_path: Path
    max_history_items: int

    sqlite_database_path: Path
    sqlite_connection_timeout_seconds: float
    sqlite_echo_sql: bool

    theme: str

    @property
    def is_development(self) -> bool:
        return self.app_env.lower() in {"development", "develop", "dev", "local"}

    @property
    def is_sqlite_history_enabled(self) -> bool:
        return self.history_storage_type.lower() == "sqlite"


@lru_cache
def get_settings(env_file: Path = DEFAULT_ENV_FILE) -> DesktopSettings:
    file_values = _read_env_file(env_file)

    return DesktopSettings(
        app_name=_get_env_value(file_values, "APP_NAME", "Queue Analysis Desktop"),
        app_env=_get_env_value(file_values, "APP_ENV", "development"),
        log_level=_get_env_value(file_values, "LOG_LEVEL", "INFO"),

        api_base_url=_get_env_value(
            file_values,
            "API_BASE_URL",
            "http://localhost:8000/api/v1",
        ),
        request_timeout_seconds=_parse_float(
            _get_env_value(file_values, "REQUEST_TIMEOUT_SECONDS", "10"),
            default=10.0,
        ),

        history_storage_type=_get_env_value(
            file_values,
            "HISTORY_STORAGE_TYPE",
            "sqlite",
        ),
        history_json_path=_resolve_project_path(
            _get_env_value(file_values, "HISTORY_JSON_PATH", "./data/history.json")
        ),
        max_history_items=_parse_int(
            _get_env_value(file_values, "MAX_HISTORY_ITEMS", "50"),
            default=50,
        ),

        sqlite_database_path=_resolve_project_path(
            _get_env_value(
                file_values,
                "SQLITE_DATABASE_PATH",
                "./data/history.sqlite3",
            )
        ),
        sqlite_connection_timeout_seconds=_parse_float(
            _get_env_value(file_values, "SQLITE_CONNECTION_TIMEOUT_SECONDS", "5"),
            default=5.0,
        ),
        sqlite_echo_sql=_parse_bool(
            _get_env_value(file_values, "SQLITE_ECHO_SQL", "false")
        ),

        theme=_get_env_value(file_values, "THEME", "system"),
    )
