# Queue Analysis API

FastAPI-сервер для анализа одноканальной системы массового обслуживания **M/M/1**.

Сервер принимает параметры системы, выполняет расчет характеристик и возвращает результат через REST API.

Сервер **не хранит историю расчетов**. История хранится локально на стороне клиентов:

```text
client-web     → Pinia/localStorage
client-desktop → SQLite через SQLAlchemy ORM
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

## CORS

В development-режиме:

```env
APP_ENV=development
```

сервер разрешает запросы со всех origins.

В publish-режиме:

```env
APP_ENV=publish
CORS_ORIGINS=https://example.com,https://www.example.com
```

сервер разрешает запросы только с адресов из `CORS_ORIGINS`.

## Локальный запуск

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

## API endpoint-ы

```text
GET  /health
POST /api/v1/queue/analyze
GET  /api/v1/queue/formulas
```

Endpoint `/api/v1/queue/default` не используется.

### GET /health

```json
{
  "status": "ok",
  "service": "Queue Analysis API",
  "environment": "development"
}
```

### POST /api/v1/queue/analyze

Запрос:

```json
{
  "lambda_rate": 6,
  "mu_rate": 8
}
```

Ответ:

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

Для неустойчивой системы `average_*` поля возвращаются как `null`.

### GET /api/v1/queue/formulas

```json
{
  "model_name": "M/M/1",
  "description": "Одноканальная система массового обслуживания с пуассоновским потоком заявок и экспоненциальным временем обслуживания.",
  "stability_condition": "λ < μ",
  "formulas": {
    "utilization": "ρ = λ / μ",
    "average_orders_in_system": "L = λ / (μ - λ)",
    "average_waiting_time": "Wq = λ / (μ * (μ - λ))",
    "average_time_in_system": "W = 1 / (μ - λ)"
  }
}
```

## Тестирование

```bash
cd server
pytest
```

Тесты покрывают:

- расчетный сервис;
- FastAPI endpoint-ы;
- CORS-конфигурацию;
- актуальный контракт ответа для клиентов.

## Docker

Сборка из папки `server`:

```bash
docker build -t queue-analysis-server .
```

Запуск:

```bash
docker run --rm -p 8000:8000 --env-file .env queue-analysis-server
```

При запуске через `docker compose` из корня проекта сервер использует `server/.env`.

## Важные ограничения

- Сервер не хранит историю расчетов.
- Сервер не использует глобальную БД.
- Сервер не отвечает за UI.
- Серверный контракт должен совпадать с DTO web- и desktop-клиентов.
