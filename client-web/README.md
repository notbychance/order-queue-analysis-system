# Queue Analysis Web Client

Web-клиент системы анализа одноканальной системы массового обслуживания **M/M/1**.

Клиент реализован на **Vue 3 + Vite + TypeScript** и обращается к FastAPI-серверу для расчета показателей. История расчетов хранится локально в браузере через **Pinia + localStorage**.

Сервер историю не хранит.

## Основные возможности

- ввод интенсивности поступления заказов `λ`;
- ввод интенсивности обслуживания `μ`;
- расчет через FastAPI;
- отображение результата анализа;
- отображение формул модели M/M/1;
- локальная история расчетов;
- повтор расчета из истории;
- удаление и очистка истории;
- импорт/экспорт истории в JSON;
- светлая и темная тема;
- SVG-графики чувствительности системы;
- unit-тесты компонентов, stores, сервисов и утилит.

## Стек

- Vue 3
- Vite
- TypeScript
- Vue Router
- Pinia
- pinia-plugin-persistedstate
- Axios
- Naive UI
- Vitest
- Vue Test Utils

## Требования

- Node.js `20.19+` или `22.12+`;
- npm.

Версии указаны в `package.json`.

## Установка

```bash
cd client-web
npm install
```

В Docker используется:

```bash
npm ci
```

Поэтому `package.json` и `package-lock.json` должны быть актуальными.

## Переменные окружения

Создай локальный `.env` на основе `.env.example`.

Для локальной разработки через Vite:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_REQUEST_TIMEOUT_MS=10000
VITE_APP_NAME=Queue Analysis Web
```

Для Docker/nginx-сборки:

```env
VITE_API_BASE_URL=/api/v1
```

В этом режиме nginx проксирует `/api/...` в FastAPI.

## Локальный запуск

Сначала запусти FastAPI-сервер:

```bash
cd server
uvicorn app.main:app --reload
```

Потом web-клиент:

```bash
cd client-web
npm run dev
```

Адрес Vite:

```text
http://localhost:5173
```

## Сборка

```bash
npm run build
```

Скрипт выполняет type-check и production-сборку.

Отдельно:

```bash
npm run type-check
npm run build-only
```

## Тесты

```bash
npm run test:unit
```

## Линтинг и форматирование

```bash
npm run lint
npm run format
```

## Docker

Сборка образа из папки `client-web`:

```bash
docker build -t queue-analysis-web .
```

Запуск отдельно:

```bash
docker run --rm -p 8080:80 queue-analysis-web
```

Адрес:

```text
http://localhost:8080
```

Для полноценной работы web-клиент должен запускаться вместе с FastAPI, чтобы nginx мог проксировать API-запросы на сервис `server`.

## API

Web-клиент использует:

```text
POST /api/v1/queue/analyze
GET  /api/v1/queue/formulas
```

### Request DTO

```json
{
  "lambda_rate": 6,
  "mu_rate": 8
}
```

### Response DTO

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

Важно: web-клиент ожидает поле `utilization`, а не старое поле `rho`.

## CORS

При локальном запуске Vite использует origin:

```text
http://localhost:5173
```

На сервере для разработки должен быть включен:

```env
APP_ENV=development
```

В Docker/nginx-сценарии web-клиент обращается к API через относительный путь `/api/v1`, поэтому запросы идут на тот же origin.

## Структура

```text
client-web/
├── src/
│   ├── api/          # axios-клиент и API-методы
│   ├── assets/       # CSS и темы
│   ├── components/   # Vue-компоненты
│   ├── config/       # Vite env
│   ├── router/       # маршруты
│   ├── services/     # импорт/экспорт истории
│   ├── stores/       # Pinia-store
│   ├── types/        # TypeScript DTO
│   ├── utils/        # форматирование
│   └── views/        # страницы
├── tests/
├── Dockerfile
├── nginx.conf
├── package.json
├── package-lock.json
├── vite.config.ts
├── vitest.config.ts
└── README.md
```

## Локальная история

История хранится только в браузере пользователя.

Сохраняются:

- дата расчета;
- параметры `λ` и `μ`;
- полный ответ сервера;
- статус устойчивости;
- расчетные показатели.

Историю можно экспортировать в JSON и импортировать обратно.
