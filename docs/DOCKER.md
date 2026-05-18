# Docker

Докеризация проекта настроена для полного запуска серверной части и web-клиента.

Desktop-клиент на PySide6/QML не запускается как GUI-приложение через Docker, потому что ему нужно графическое окружение. Для desktop-модуля Docker используется для проверки зависимостей и тестов.

## Сервисы

```text
server              FastAPI API
client-web          Vue production build через nginx
server-tests        тесты server, профиль test
client-web-tests    тесты client-web, профиль test
client-desktop-tests тесты client-desktop, профиль test
```

## Полный запуск приложения

Из корня проекта:

```bash
docker compose up --build
```

После запуска:

```text
Web:     http://localhost:8080
FastAPI: http://localhost:8000
Swagger: http://localhost:8000/docs
Health:  http://localhost:8000/health
```

Web-клиент в Docker обращается к API через относительный путь:

```text
/api/v1
```

Nginx внутри контейнера `client-web` проксирует запросы `/api/...` на сервис:

```text
http://server:8000/api/...
```

## Остановка

```bash
docker compose down
```

Остановка с удалением образов и orphan-контейнеров:

```bash
docker compose down --remove-orphans
```

## Переменные окружения docker-compose

`docker-compose.yml` использует значения по умолчанию, поэтому отдельный `.env` в корне не обязателен.

При необходимости можно переопределить:

```env
SERVER_PORT=8000
WEB_PORT=8080

SERVER_APP_ENV=development
SERVER_DEBUG=false
SERVER_API_PREFIX=/api/v1
SERVER_LOG_LEVEL=INFO

WEB_API_BASE_URL=/api/v1
WEB_REQUEST_TIMEOUT_MS=10000
WEB_APP_NAME=Queue Analysis Web
```

Пример запуска с другим портом web-клиента:

```bash
WEB_PORT=8090 docker compose up --build
```

На Windows PowerShell:

```powershell
$env:WEB_PORT = "8090"
docker compose up --build
```

## Тесты всех модулей в Docker

Запуск тестовых контейнеров:

```bash
docker compose --profile test up --build --abort-on-container-exit
```

Удалить контейнеры после тестов:

```bash
docker compose --profile test down --remove-orphans
```

Можно запускать тесты по отдельности.

### Server tests

```bash
docker compose --profile test run --rm server-tests
```

### Web tests

```bash
docker compose --profile test run --rm client-web-tests
```

### Desktop tests

```bash
docker compose --profile test run --rm client-desktop-tests
```

## Почему у server нет volume с data

Сервер FastAPI не хранит историю и не использует глобальную БД. Поэтому volume вида:

```yaml
./server/data:/app/data
```

не нужен.

История хранится локально:

```text
client-web     localStorage
client-desktop SQLite
```

## CORS в Docker

В Docker web-клиент обращается к API через nginx-прокси на том же origin:

```text
http://localhost:8080/api/v1
```

Поэтому CORS для этого сценария обычно не мешает.

Для локальной разработки без nginx, когда Vue работает на `http://localhost:5173`, сервер можно запускать с:

```env
APP_ENV=development
```

В этом режиме сервер разрешает все origins.
