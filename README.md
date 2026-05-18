# Order Queue Analysis System

Клиент-серверная система для анализа одноканальной системы массового обслуживания **M/M/1**.

Проект состоит из трех модулей:

```text
order queue analysis system/
├── server/           # FastAPI API для расчета и формул
├── client-web/       # Vue 3 web-клиент
├── client-desktop/   # PySide6/QML desktop-клиент
├── docs/             # общая документация по контракту API
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

## API-контракт

Основные endpoint-ы:

```text
GET  /health
POST /api/v1/queue/analyze
GET  /api/v1/queue/formulas
```

Endpoint `/api/v1/queue/default` не используется.

Общий DTO ответа `POST /api/v1/queue/analyze` для web- и desktop-клиентов:

```json
{
  "lambda_rate": 6.0,
  "mu_rate": 8.0,
  "arrival_rate_unit": "заказов/день",
  "service_rate_unit": "заказов/день",
  "time_unit": "дней",
  "is_stable": true,
  "utilization": 0.75,
  "utilization_percent": 75.0,
  "average_orders_in_system": 3.0,
  "average_waiting_time": 0.375,
  "average_waiting_time_hours": 9.0,
  "average_time_in_system": 0.5,
  "average_time_in_system_hours": 12.0,
  "conclusion": "Система устойчива. Клерк загружен на 75.0%. Очередь не растет неограниченно."
}
```

Подробнее: [`docs/API_CONTRACT.md`](docs/API_CONTRACT.md).

## Локальный запуск

### 1. Сервер

```bash
cd server
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Установка зависимостей:

```bash
pip install -r requirements.txt
```

Запуск:

```bash
uvicorn app.main:app --reload
```

Проверка:

```text
http://localhost:8000/health
http://localhost:8000/docs
```

### 2. Web-клиент

```bash
cd client-web
npm install
npm run dev
```

По умолчанию Vite запускает приложение на:

```text
http://localhost:5173
```

Для локальной разработки в `client-web/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### 3. Desktop-клиент

```bash
cd client-desktop
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Установка зависимостей:

```bash
pip install -r requirements-dev.txt
```

Запуск:

```bash
python -m app.main
```

По умолчанию desktop-клиент обращается к API:

```text
http://localhost:8000/api/v1
```

## Docker

Сервер и web-клиент могут запускаться через Docker. Desktop-клиент запускается локально, потому что GUI-приложение PySide6/QML требует графического окружения.

Из корня проекта:

```bash
docker compose up --build
```

После запуска:

```text
FastAPI: http://localhost:8000
Swagger: http://localhost:8000/docs
Web:     http://localhost:8080
```

Остановка:

```bash
docker compose down
```

## Тесты

### Server

```bash
cd server
pytest
```

### Client web

```bash
cd client-web
npm run test:unit
npm run type-check
npm run build
```

### Client desktop

```bash
cd client-desktop
pytest
```

## Сборка desktop EXE

```powershell
cd client-desktop
.\scripts\build_exe.ps1
```

Результат:

```text
client-desktop/dist/QueueAnalysisDesktop/QueueAnalysisDesktop.exe
```

## Переменные окружения

В Git хранятся только `.env.example`.

Локальные `.env` файлы не должны коммититься:

```text
server/.env
client-web/.env
client-desktop/.env
```

## Что важно для защиты

- Сервер выполняет расчет и не хранит историю.
- Web-клиент хранит историю локально в браузере.
- Desktop-клиент хранит историю локально в SQLite.
- Web и desktop используют одинаковый API-контракт.
- Есть unit/API-тесты для сервера.
- Есть unit-тесты web-клиента.
- Есть unit-тесты desktop-клиента, включая слой SQLite/SQLAlchemy и ViewModel.
- Есть Dockerfile для каждого модуля.
- Desktop-клиент можно собрать в `.exe`.
