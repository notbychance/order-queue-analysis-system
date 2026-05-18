# Queue Analysis Desktop

Desktop-клиент клиент-серверной системы анализа одноканальной системы массового обслуживания.

## Стек

- Python
- PySide6 / QML / Qt Quick
- httpx
- Pydantic
- SQLAlchemy ORM
- SQLite
- pytest
- PyInstaller

FastAPI-сервер выполняет расчет модели M/M/1, а desktop-клиент сохраняет историю локально в SQLite. Глобальная БД на сервере не используется.

## Структура модуля

```text
client-desktop/
├── app/
│   ├── api/                 # HTTP-клиент FastAPI
│   ├── core/                # настройки .env
│   ├── data/                # SQLAlchemy, ORM-модели, репозитории
│   ├── schemas/             # Pydantic DTO
│   ├── services/            # сервисы истории
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
└── QueueAnalysisDesktop.spec
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

## Локальная история

История расчетов хранится только на стороне desktop-клиента.

По умолчанию SQLite-файл создается здесь:

```text
client-desktop/data/history.sqlite3
```

Сервер FastAPI историю не хранит.

## Тесты

```powershell
cd client-desktop
pytest
```

## Docker

Dockerfile для desktop-модуля предназначен в первую очередь для проверки тестов и зависимостей в изолированной Linux-среде.

Собрать образ:

```bash
cd client-desktop
docker build -t queue-analysis-desktop .
```

Запустить тесты:

```bash
docker run --rm queue-analysis-desktop
```

Или явно:

```bash
docker run --rm queue-analysis-desktop pytest
```

Полноценный запуск GUI-приложения из Docker не является основным сценарием, потому что PySide6/QML требует графического окружения. Для разработки и защиты курсовой desktop-клиент запускается локально на Windows, а Docker используется для проверки сборки зависимостей и тестов.

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

Результат:

```text
client-desktop/dist/QueueAnalysisDesktop/QueueAnalysisDesktop.exe
```

После сборки `.env` можно положить рядом с `QueueAnalysisDesktop.exe`, если нужно изменить `API_BASE_URL`, путь SQLite-БД или тему без пересборки.

## Основные функции

- ввод интенсивности поступления заказов `λ`;
- ввод интенсивности обслуживания `μ`;
- отправка параметров на FastAPI;
- отображение результатов анализа;
- график чувствительности;
- локальная история расчетов в SQLite;
- импорт/экспорт истории в JSON;
- светлая/темная/system-тема;
- сборка Windows `.exe`.
