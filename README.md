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

## Быстрый старт

```bash
docker compose up --build
```

После запуска:

```text
Web:     http://localhost:8080
FastAPI: http://localhost:8000
Swagger: http://localhost:8000/docs
```

Полная инструкция по использованию:

```text
docs/USAGE.md
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

## Документация

```text
docs/USAGE.md              инструкция по использованию
docs/API_CONTRACT.md       API-контракт
docs/DOCKER.md             Docker-запуск
docs/DOCKER_PUBLISHING.md  публикация Docker images в GHCR
docs/INTEGRATION_TESTS.md  интеграционные тесты
docs/CI.md                 CI
docs/RELEASE_WORKFLOW.md   GitHub Release workflow
```

## API

```text
GET  /health
POST /api/v1/queue/analyze
GET  /api/v1/queue/formulas
```

Endpoint `/api/v1/queue/default` не используется.

## История расчетов

```text
server         не хранит историю
client-web     localStorage
client-desktop SQLite
```

## Тесты через Docker

```bash
docker compose --profile test up --build --abort-on-container-exit
```
