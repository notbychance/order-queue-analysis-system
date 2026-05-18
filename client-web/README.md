# client-web

Web-клиент информационной системы анализа одноканальной системы массового обслуживания.

Клиент реализован на Vue 3 и обращается к FastAPI-серверу для расчета показателей модели M/M/1. История расчетов хранится локально в браузере через Pinia и `localStorage`. Сервер историю не хранит.

## Основные возможности

- ввод интенсивности поступления заявок `λ`;
- ввод интенсивности обслуживания `μ`;
- отправка параметров на FastAPI;
- отображение результата анализа;
- отображение формул модели M/M/1;
- локальная история расчетов;
- импорт и экспорт истории в JSON;
- светлая и темная тема;
- график зависимости показателей системы от `λ`;
- unit-тесты компонентов, store, сервисов и утилит.

## Требования

Для локальной разработки:

- Node.js версии `20.19+` или `22.12+`;
- npm.

Версии также указаны в поле `engines` файла `package.json`.

## Установка зависимостей

```bash
npm install
```

В Docker используется команда:

```bash
npm ci
```

Она устанавливает зависимости строго по `package-lock.json`, поэтому перед сборкой Docker важно, чтобы `package.json` и `package-lock.json` были актуальными.

## Переменные окружения

Создай локальный файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Для локальной разработки через Vite обычно используется полный адрес API:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_REQUEST_TIMEOUT_MS=10000
VITE_APP_NAME=Queue Analysis Web
```

Для Docker/nginx-сборки используется относительный адрес:

```env
VITE_API_BASE_URL=/api/v1
```

В этом случае браузер обращается к тому же origin, где открыт web-клиент, а nginx проксирует `/api/...` в контейнер FastAPI.

## Локальный запуск

Перед запуском web-клиента должен быть запущен FastAPI-сервер на `http://localhost:8000`.

```bash
npm run dev
```

По умолчанию Vite откроет приложение на:

```text
http://localhost:5173
```

## Сборка

```bash
npm run build
```

Скрипт выполняет проверку типов и сборку Vite.

## Preview production-сборки

```bash
npm run preview
```

## Тесты

```bash
npm run test:unit
```

Тесты запускаются через Vitest. Конфигурация находится в `vitest.config.ts`.

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

После запуска приложение будет доступно по адресу:

```text
http://localhost:8080
```

Для полноценной работы через Docker рекомендуется запускать web-клиент вместе с FastAPI через `docker-compose.yml` из корня проекта, чтобы nginx мог проксировать запросы на сервис `server`.

## API

Web-клиент использует endpoint-ы FastAPI:

```text
POST /api/v1/queue/analyze
GET  /api/v1/queue/formulas
```

Endpoint `POST /api/v1/queue/analyze` принимает:

```json
{
  "lambda_rate": 6,
  "mu_rate": 8
}
```

И возвращает результат анализа системы:

- устойчивость системы;
- коэффициент загрузки;
- среднее число заявок в системе;
- среднее время ожидания;
- среднее время пребывания заявки в системе;
- текстовое заключение.

## CORS

При локальном запуске через Vite запросы идут с origin `http://localhost:5173`. На стороне FastAPI для разработки должен быть включен режим:

```env
APP_ENV=development
```

В этом режиме сервер пропускает origins для разработки.

В Docker/nginx-сценарии web-клиент обращается к API через относительный путь `/api/v1`, поэтому запросы идут на тот же origin, а nginx проксирует их в FastAPI. Это снижает необходимость в CORS для браузера при publish-запуске.

## Структура

```text
client-web/
├── src/
│   ├── api/          # axios-клиент и API-методы
│   ├── assets/       # CSS и темы
│   ├── components/   # Vue-компоненты
│   ├── config/       # чтение Vite env
│   ├── router/       # маршруты Vue Router
│   ├── services/     # сервисы, например импорт/экспорт истории
│   ├── stores/       # Pinia-store
│   ├── types/        # TypeScript-типы DTO
│   ├── utils/        # утилиты форматирования
│   └── views/        # страницы приложения
├── Dockerfile
├── nginx.conf
├── .dockerignore
├── package.json
└── package-lock.json
```
