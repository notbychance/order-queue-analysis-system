# Queue Analysis Desktop

Desktop-клиент клиент-серверной системы анализа одноканальной системы массового обслуживания.

Технологии:

- Python
- PySide6 / QML / Qt Quick
- httpx
- SQLAlchemy
- SQLite
- PyInstaller

FastAPI-сервер выполняет расчет модели M/M/1, а desktop-клиент сохраняет историю локально в SQLite. Глобальная БД на сервере не используется.

## Локальный запуск

```bash
cd client-desktop
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
python -m app.main
```

Перед расчетом должен быть запущен FastAPI-сервер:

```bash
cd server
uvicorn app.main:app --reload
```

По умолчанию desktop-клиент обращается к API:

```text
http://localhost:8000/api/v1
```

## Настройки

Локальные настройки лежат в `.env`.

Пример:

```env
APP_NAME=Queue Analysis Desktop
APP_ENV=development
API_BASE_URL=http://localhost:8000/api/v1
REQUEST_TIMEOUT_SECONDS=10

HISTORY_STORAGE_TYPE=sqlite
MAX_HISTORY_ITEMS=50
SQLITE_DATABASE_PATH=./data/history.sqlite3
SQLITE_CONNECTION_TIMEOUT_SECONDS=5
SQLITE_ECHO_SQL=false

THEME=system
```

После сборки `.exe` файл `.env` можно положить рядом с `QueueAnalysisDesktop.exe`, если нужно изменить настройки без пересборки.

## Тесты

```bash
cd client-desktop
pytest
```

## Сборка EXE

Для сборки используется PyInstaller.

PowerShell:

```powershell
cd client-desktop
.\scripts\build_exe.ps1
```

CMD:

```bat
cd client-desktop
scripts\build_exe.bat
```

Результат будет в папке:

```text
client-desktop/dist/QueueAnalysisDesktop/
```

Запуск:

```text
client-desktop/dist/QueueAnalysisDesktop/QueueAnalysisDesktop.exe
```

## Что попадает в сборку

В сборку включаются:

- Python-код приложения;
- QML-файлы интерфейса;
- библиотеки PySide6;
- SQLAlchemy/httpx/Pydantic;
- `.env.example`.

Файл `.env` не обязан попадать в сборку. Его можно создать вручную рядом с `.exe`.

## Локальная история

История расчетов хранится в SQLite на стороне desktop-клиента.

По умолчанию:

```text
./data/history.sqlite3
```

Для собранного приложения относительный путь считается от папки рядом с `.exe`.
