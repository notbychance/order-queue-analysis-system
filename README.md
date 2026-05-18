# Order Queue Analysis System

Клиент-серверная система для анализа одноканальной системы массового обслуживания **M/M/1**.

Проект состоит из трех модулей:

```text
order queue analysis system/
├── server/           # FastAPI API для расчета и формул
├── client-web/       # Vue 3 web-клиент
├── client-desktop/   # PySide6/QML desktop-клиент
├── docs/             # документация
└── docker-compose.yml
```

## Архитектура

```text
client-web
  ├─ хранит историю локально в браузере через Pinia/localStorage
  └─ обращается к FastAPI по HTTP

client-desktop
  ├─ хранит историю локально в SQLite через SQLAlchemy ORM
  └─ обращается к FastAPI по HTTP

server
  ├─ выполняет расчет модели M/M/1
  ├─ возвращает формулы модели
  └─ не хранит глобальную историю расчетов
```

Глобальной БД на сервере нет. История расчетов хранится только на стороне клиентов.

## Быстрый запуск через Docker

Из корня проекта:

```bash
docker compose up --build
```

После запуска:

```text
Web:     http://localhost:8080
FastAPI: http://localhost:8000
Swagger: http://localhost:8000/docs
```

Подробнее: [`docs/DOCKER.md`](docs/DOCKER.md).

## Тесты через Docker

```bash
docker compose --profile test up --build --abort-on-container-exit
```

Или по отдельности:

```bash
docker compose --profile test run --rm server-tests
docker compose --profile test run --rm client-web-tests
docker compose --profile test run --rm client-desktop-tests
```

## Локальный запуск

### Server

```bash
cd server
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Web

```bash
cd client-web
npm install
npm run dev
```

### Desktop

```bash
cd client-desktop
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
python -m app.main
```

## API

```text
GET  /health
POST /api/v1/queue/analyze
GET  /api/v1/queue/formulas
```

Endpoint `/api/v1/queue/default` не используется.

Актуальный контракт: [`docs/API_CONTRACT.md`](docs/API_CONTRACT.md).

## История расчетов

```text
server         не хранит историю
client-web     localStorage
client-desktop SQLite
```

## Desktop EXE

```powershell
cd client-desktop
.\scripts\build_exe.ps1
```

Результат:

```text
client-desktop/dist/QueueAnalysisDesktop/QueueAnalysisDesktop.exe
```
