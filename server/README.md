# Queue Analysis API

FastAPI-сервер для анализа одноканальной системы массового обслуживания **M/M/1**.

Сервер принимает параметры системы, выполняет расчет характеристик и возвращает результат через REST API.

Сервер **не хранит историю расчетов**. История хранится локально на стороне клиентов:

```text
client-web     → Pinia/localStorage
client-desktop → SQLite через SQLAlchemy ORM
```

## Зависимости

Зависимости разделены на runtime и development/test:

```text
requirements.txt      зависимости обычного запуска API
requirements-dev.txt  зависимости тестов и разработки
```

Для запуска сервера достаточно:

```bash
pip install -r requirements.txt
```

Для разработки и тестов:

```bash
pip install -r requirements-dev.txt
```

## Основные возможности

- расчет характеристик модели M/M/1;
- проверка устойчивости системы по условию `λ < μ`;
- расчет коэффициента загрузки `utilization`;
- расчет среднего числа заказов в системе `L`;
- расчет среднего времени ожидания `Wq`;
- расчет среднего времени пребывания в системе `W`;
- перевод времени из дней в часы;
- получение справки по формулам модели;
- CORS-режимы для development и publish.

## Структура серверного модуля

```text
server/
├── app/
│   ├── api/v1/queue.py
│   ├── core/config.py
│   ├── schemas/queue.py
│   ├── services/queue_analysis.py
│   └── main.py
├── tests/
├── .env.example
├── .dockerignore
├── Dockerfile
├── pytest.ini
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

## Переменные окружения

Создай локальный `.env`:

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Пример:

```env
APP_NAME=Queue Analysis API
APP_ENV=development
DEBUG=true

API_PREFIX=/api/v1

CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:8080,http://127.0.0.1:8080
CORS_ALLOW_CREDENTIALS=false

LOG_LEVEL=INFO
```

## Локальный запуск

```bash
cd server
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Установка runtime-зависимостей:

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

## Тестирование

Для тестов установи dev-зависимости:

```bash
pip install -r requirements-dev.txt
pytest
```

Тесты покрывают:

- расчетный сервис;
- FastAPI endpoint-ы;
- CORS-конфигурацию;
- актуальный контракт ответа для клиентов;
- интеграционные проверки API-контракта.

## API endpoint-ы

```text
GET  /health
POST /api/v1/queue/analyze
GET  /api/v1/queue/formulas
```

Endpoint `/api/v1/queue/default` не используется.

## Docker

Production-like сборка сервера использует только `requirements.txt`.

```bash
docker build --target runtime -t queue-analysis-server .
```

Запуск:

```bash
docker run --rm -p 8000:8000 --env-file .env queue-analysis-server
```

Тестовая сборка использует `requirements-dev.txt`:

```bash
docker build --target test -t queue-analysis-server-tests .
docker run --rm queue-analysis-server-tests
```

При запуске через `docker compose` из корня проекта targets выбираются автоматически:

```bash
docker compose up --build
docker compose --profile test up --build --abort-on-container-exit
```

## Важные ограничения

- Сервер не хранит историю расчетов.
- Сервер не использует глобальную БД.
- Сервер не отвечает за UI.
- Серверный контракт должен совпадать с DTO web- и desktop-клиентов.
