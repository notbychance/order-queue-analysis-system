# Integration tests

Проект содержит unit-тесты и интеграционные тесты.

Интеграционные тесты проверяют не отдельную функцию, а связку нескольких слоев.

## Server

Файл:

```text
server/tests/integration/test_queue_api_contract.py
```

Проверяется полный путь FastAPI:

```text
HTTP request
↓
FastAPI endpoint
↓
Pydantic request DTO
↓
расчетный сервис
↓
Pydantic response DTO
↓
HTTP response
```

Также проверяется, что серверный контракт совпадает с DTO клиентов:

```text
utilization есть
rho отсутствует
rate_unit отсутствует
rate_unit_label отсутствует
time_unit_label отсутствует
message отсутствует
```

Запуск:

```bash
cd server
pytest -m integration
```

## Client web

Файл:

```text
client-web/src/test/integration/queueAnalysisFlow.spec.ts
```

Проверяется связка:

```text
Pinia store
↓
queueApi mock
↓
current FastAPI response contract
↓
local history
```

Запуск:

```bash
cd client-web
npm run test:unit -- --run src/test/integration
```

Обычный запуск всех тестов:

```bash
npm run test:unit
```

## Client desktop

Файл:

```text
client-desktop/tests/integration/test_queue_api_history_flow.py
```

Проверяется связка:

```text
QueueApiClient
↓
Pydantic DTO ответа FastAPI
↓
HistoryService
↓
HistoryRepository
↓
SQLAlchemy
↓
локальная SQLite-БД
```

Запуск:

```bash
cd client-desktop
pytest -m integration
```

Обычный запуск всех тестов:

```bash
pytest
```

## Все тесты через Docker

```bash
docker compose --profile test up --build --abort-on-container-exit
```

Интеграционные тесты входят в общий запуск `pytest` / `vitest`.
