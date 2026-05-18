# Queue Analysis API

FastAPI-сервер для курсовой работы по анализу одноканальной системы массового обслуживания M/M/1.

Сервер принимает параметры системы, выполняет расчет характеристик и возвращает результат через REST API. Сервер не хранит историю расчетов: история ведется локально на стороне клиентов.

## Основные возможности

- анализ системы массового обслуживания M/M/1;
- расчет коэффициента загрузки клерка;
- расчет среднего числа заказов в системе;
- расчет среднего времени ожидания начала обработки;
- расчет среднего времени пребывания заказа в системе;
- проверка устойчивости системы по условию `λ < μ`;
- получение справки по используемым формулам;
- настройка CORS для режимов разработки и публикации.

## Структура серверного модуля

```text
server/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── queue.py
│   ├── core/
│   │   └── config.py
│   ├── schemas/
│   │   └── queue.py
│   ├── services/
│   │   └── queue_analysis.py
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

Создай локальный файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Для Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Пример локальной конфигурации:

```env
APP_NAME=Queue Analysis API
APP_ENV=development
DEBUG=true
API_PREFIX=/api/v1
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:8080,http://127.0.0.1:8080
CORS_ALLOW_CREDENTIALS=false
LOG_LEVEL=INFO
```

### Режимы CORS

В режиме разработки:

```env
APP_ENV=development
```

сервер разрешает запросы со всех origins.

В режиме публикации:

```env
APP_ENV=publish
CORS_ORIGINS=https://example.com,https://www.example.com
```

сервер разрешает запросы только с адресов, указанных в `CORS_ORIGINS`.

## Локальный запуск

Создай и активируй виртуальное окружение:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Установи зависимости:

```bash
pip install -r requirements.txt
```

Запусти сервер:

```bash
uvicorn app.main:app --reload
```

После запуска доступны:

```text
API:     http://localhost:8000
Swagger: http://localhost:8000/docs
Health:  http://localhost:8000/health
```

## API endpoint-ы

### Проверка состояния сервера

```http
GET /health
```

Пример ответа:

```json
{
  "status": "ok",
  "service": "Queue Analysis API",
  "environment": "development"
}
```

### Анализ системы

```http
POST /api/v1/queue/analyze
Content-Type: application/json

{
  "lambda_rate": 6,
  "mu_rate": 8
}
```

Пример ответа:

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

### Формулы модели

```http
GET /api/v1/queue/formulas
```

Возвращает название модели, условие устойчивости и формулы расчета.

## Тестирование

Запуск всех тестов:

```bash
pytest
```

Запуск с отчетом покрытия:

```bash
pytest --cov=app --cov-report=term-missing
```

Тесты включают:

- unit-тесты расчетного сервиса;
- API-тесты FastAPI endpoint-ов;
- тесты конфигурации CORS.

## Docker

Сборка образа из папки `server`:

```bash
docker build -t queue-analysis-server .
```

Запуск контейнера:

```bash
docker run --rm -p 8000:8000 --env-file .env queue-analysis-server
```

При запуске через `docker compose` из корня проекта сервер использует тот же `.env` файл, если он подключен в `docker-compose.yml` через `env_file`.
