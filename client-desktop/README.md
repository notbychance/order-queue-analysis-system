# Queue Analysis Desktop Client

Desktop-клиент системы анализа одноканальной системы массового обслуживания **M/M/1**.

Клиент реализован на **PySide6 + QML / Qt Quick**. Расчет выполняется на FastAPI-сервере, а история расчетов хранится локально в SQLite через **SQLAlchemy ORM**.

Сервер историю не хранит.

## Стек

- Python
- PySide6 / QML / Qt Quick
- httpx
- Pydantic
- SQLAlchemy ORM
- SQLite
- pytest
- pytest-qt
- respx
- PyInstaller

## Основные возможности

- ввод интенсивности поступления заказов `λ`;
- ввод интенсивности обслуживания `μ`;
- расчет через FastAPI;
- отображение результатов анализа;
- график чувствительности;
- локальная история расчетов в SQLite;
- повтор расчета из истории;
- удаление и очистка истории;
- импорт/экспорт истории в JSON;
- светлая/темная/system-тема;
- сохранение темы через QSettings;
- сборка Windows `.exe`.

## Структура модуля

```text
client-desktop/
├── app/
│   ├── api/                 # HTTP-клиент FastAPI
│   ├── core/                # чтение .env
│   ├── data/                # SQLAlchemy, ORM-модели, репозитории
│   ├── schemas/             # Pydantic DTO
│   ├── services/            # сервисы истории и JSON-файлов
│   ├── ui/qml/              # QML-интерфейс
│   ├── viewmodels/          # ViewModel для QML
│   └── main.py
├── tests/
├── scripts/
├── requirements.txt
├── requirements-dev.txt
├── pytest.ini
├── Dockerfile
├── .dockerignore
├── QueueAnalysisDesktop.spec
└── README.md
```

## Локальный запуск

Создать окружение:

```powershell
cd client-desktop
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
```

Запустить FastAPI-сервер в отдельном терминале:

```powershell
cd server
uvicorn app.main:app --reload
```

Запустить desktop-клиент:

```powershell
cd client-desktop
python -m app.main
```

## Настройки

Локальные настройки лежат в `.env`.

Пример:

```env
APP_NAME=Queue Analysis Desktop
APP_ENV=development
LOG_LEVEL=INFO

API_BASE_URL=http://localhost:8000/api/v1
REQUEST_TIMEOUT_SECONDS=10

HISTORY_STORAGE_TYPE=sqlite
MAX_HISTORY_ITEMS=50

HISTORY_JSON_PATH=./data/history.json

SQLITE_DATABASE_PATH=./data/history.sqlite3
SQLITE_CONNECTION_TIMEOUT_SECONDS=5
SQLITE_ECHO_SQL=false

THEME=system
```

`.env.example` можно хранить в Git, `.env` обычно не коммитится.

## API-контракт

Desktop-клиент использует:

```text
POST /api/v1/queue/analyze
GET  /api/v1/queue/formulas
GET  /health
```

DTO ответа анализа должен содержать поле:

```text
utilization
```

Старое поле `rho` не используется.

## Локальная история

История расчетов хранится только на стороне desktop-клиента.

По умолчанию SQLite-файл создается здесь:

```text
client-desktop/data/history.sqlite3
```

Для собранного `.exe` относительный путь считается от папки рядом с `QueueAnalysisDesktop.exe`.

## Импорт и экспорт истории

История экспортируется в JSON:

```json
{
  "version": 1,
  "exported_at": "...",
  "items": []
}
```

При импорте дубликаты по `id` пропускаются.

## Тесты

```powershell
cd client-desktop
pytest
```

Тесты покрывают:

- settings;
- SQLAlchemy connection manager;
- ORM-модель истории;
- repository;
- service;
- API-клиент;
- ViewModel анализа;
- ViewModel истории;
- ViewModel формул;
- ViewModel темы;
- импорт/экспорт истории.

## Docker

Dockerfile desktop-модуля предназначен для проверки тестов и зависимостей в изолированной Linux-среде.

Сборка:

```bash
cd client-desktop
docker build -t queue-analysis-desktop .
```

Запуск тестов:

```bash
docker run --rm queue-analysis-desktop
```

Полноценный запуск GUI из Docker не является основным сценарием, потому что PySide6/QML требует графического окружения.

## Сборка EXE

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

Результат:

```text
client-desktop/dist/QueueAnalysisDesktop/QueueAnalysisDesktop.exe
```

После сборки `.env` можно положить рядом с `QueueAnalysisDesktop.exe`, если нужно изменить:

- `API_BASE_URL`;
- путь SQLite-БД;
- тему;
- лимит истории.

## Важные ограничения

- Desktop-клиент не рассчитывает модель самостоятельно.
- Расчет выполняется на FastAPI-сервере.
- История хранится локально в SQLite.
- Глобальная БД на сервере не используется.
- QML не обращается напрямую к API или БД: для этого используются ViewModel и сервисы.
