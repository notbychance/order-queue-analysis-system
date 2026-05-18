# Инструкция по использованию проекта

Проект **Order Queue Analysis System** — клиент-серверная система для анализа одноканальной системы массового обслуживания **M/M/1**.

Состав проекта:

```text
server          FastAPI-сервер расчета
client-web      Vue web-клиент
client-desktop  PySide6/QML desktop-клиент
```

Сервер выполняет только расчет и не хранит историю.

История хранится локально:

```text
client-web      в браузере через localStorage
client-desktop  в SQLite-файле на компьютере пользователя
```

---

## 1. Быстрый запуск через Docker

Это основной способ быстро запустить сервер и web-клиент.

### Требования

Нужно установить:

```text
Docker
Docker Compose
```

### Запуск

Из корня проекта:

```bash
docker compose up --build
```

После запуска открыть:

```text
Web-клиент: http://localhost:8080
Swagger:    http://localhost:8000/docs
Health:     http://localhost:8000/health
```

### Проверка расчета

В web-клиенте ввести:

```text
λ = 6
μ = 8
```

Ожидаемый результат:

```text
Загрузка клерка: 75%
Среднее число заказов L: 3
Среднее время ожидания Wq: 9 ч
Среднее время в системе W: 12 ч
```

### Остановка

```bash
docker compose down
```

---

## 2. Запуск опубликованных Docker-образов из GHCR

Этот способ используется после публикации Docker images в GitHub Container Registry.

### Настройка `.env.prod`

Скопировать пример:

```bash
cp .env.prod.example .env.prod
```

Windows PowerShell:

```powershell
Copy-Item .env.prod.example .env.prod
```

Заполнить:

```env
GHCR_IMAGE_PREFIX=ghcr.io/<owner>/<repository>
APP_VERSION=v1.0.0
```

Пример:

```env
GHCR_IMAGE_PREFIX=ghcr.io/notbychance/order-queue-analysis-system
APP_VERSION=v1.0.0
```

### Запуск

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d
```

Открыть:

```text
Web-клиент: http://localhost:8080
Swagger:    http://localhost:8000/docs
```

### Остановка

```bash
docker compose -f docker-compose.prod.yml down
```

---

## 3. Локальный запуск сервера

### Требования

```text
Python 3.14
```

### Подготовка окружения

```bash
cd server
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

### Установка зависимостей

Для обычного запуска:

```bash
pip install -r requirements.txt
```

Для разработки и тестов:

```bash
pip install -r requirements-dev.txt
```

### Настройка `.env`

Скопировать пример:

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Минимальная конфигурация:

```env
APP_NAME=Queue Analysis API
APP_ENV=development
DEBUG=true
API_PREFIX=/api/v1
LOG_LEVEL=INFO
```

### Запуск

```bash
uvicorn app.main:app --reload
```

Открыть:

```text
http://localhost:8000/docs
```

---

## 4. Локальный запуск web-клиента

### Требования

```text
Node.js 22
npm
```

### Установка зависимостей

```bash
cd client-web
npm install
```

### Настройка `.env`

Скопировать пример:

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Для локальной разработки:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_REQUEST_TIMEOUT_MS=10000
VITE_APP_NAME=Queue Analysis Web
```

### Запуск

Сначала должен быть запущен сервер:

```bash
cd server
uvicorn app.main:app --reload
```

Затем web-клиент:

```bash
cd client-web
npm run dev
```

Открыть:

```text
http://localhost:5173
```

---

## 5. Использование web-клиента

### Анализ системы

1. Открыть страницу **Анализ**.
2. Ввести `λ` — интенсивность поступления заказов.
3. Ввести `μ` — интенсивность обслуживания заказов.
4. Нажать **Рассчитать**.

Пример:

```text
λ = 6
μ = 8
```

Web-клиент отправит запрос на сервер:

```text
POST /api/v1/queue/analyze
```

И покажет:

```text
устойчивость системы
загрузку клерка
среднее число заказов в системе
среднее время ожидания
среднее время пребывания в системе
график чувствительности
```

### История расчетов

История сохраняется локально в браузере.

Можно:

```text
повторить расчет
удалить запись
очистить историю
экспортировать историю в JSON
импортировать историю из JSON
```

### Формулы

На странице **Формулы** отображаются формулы модели M/M/1, полученные с сервера:

```text
GET /api/v1/queue/formulas
```

---

## 6. Локальный запуск desktop-клиента

### Требования

```text
Python 3.12
Windows/Linux/macOS
```

Для полноценного GUI-запуска рекомендуется Windows.

### Подготовка окружения

```bash
cd client-desktop
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

### Установка зависимостей

```bash
pip install -r requirements-dev.txt
```

### Настройка `.env`

Скопировать пример:

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Минимальная конфигурация:

```env
APP_NAME=Queue Analysis Desktop
APP_ENV=development
LOG_LEVEL=INFO

API_BASE_URL=http://localhost:8000/api/v1
REQUEST_TIMEOUT_SECONDS=10

HISTORY_STORAGE_TYPE=sqlite
MAX_HISTORY_ITEMS=50

SQLITE_DATABASE_PATH=./data/history.sqlite3
SQLITE_CONNECTION_TIMEOUT_SECONDS=5
SQLITE_ECHO_SQL=false

THEME=system
```

### Запуск

Сначала запустить сервер:

```bash
cd server
uvicorn app.main:app --reload
```

Затем desktop-клиент:

```bash
cd client-desktop
python -m app.main
```

---

## 7. Использование desktop-клиента

Desktop-клиент работает по схеме:

```text
QML UI
↓
ViewModel
↓
QueueApiClient
↓
FastAPI
↓
HistoryService
↓
SQLite
```

### Анализ системы

1. Открыть раздел **Анализ системы**.
2. Ввести `λ`.
3. Ввести `μ`.
4. Нажать **Рассчитать**.

Запрос анализа выполняется в отдельном потоке, поэтому интерфейс не должен зависать во время обращения к серверу.

### История

История хранится локально в SQLite:

```text
client-desktop/data/history.sqlite3
```

Можно:

```text
повторить расчет
удалить запись
очистить историю
импортировать историю из JSON
экспортировать историю в JSON
```

### Тема

Desktop-клиент поддерживает темы:

```text
Светлая
Темная
Как в системе
```

Выбранная тема сохраняется через `QSettings`.

---

## 8. Сборка desktop EXE

Из папки `client-desktop`:

```powershell
.\scripts\build_exe.ps1
```

Или через CMD:

```bat
scripts\build_exe.bat
```

Результат:

```text
client-desktop/dist/QueueAnalysisDesktop/QueueAnalysisDesktop.exe
```

После сборки `.env` можно положить рядом с `.exe`, если нужно изменить адрес API или путь SQLite-БД:

```text
client-desktop/dist/QueueAnalysisDesktop/.env
```

---

## 9. Тестирование

### Server

```bash
cd server
pip install -r requirements-dev.txt
pytest
```

Только интеграционные тесты:

```bash
pytest -m integration
```

### Client web

```bash
cd client-web
npm install
npm run test:unit
npm run type-check
npm run build
```

### Client desktop

```bash
cd client-desktop
pip install -r requirements-dev.txt
pytest
```

Только интеграционные тесты:

```bash
pytest -m integration
```

### Все тесты через Docker

Из корня проекта:

```bash
docker compose --profile test up --build --abort-on-container-exit
```

После проверки:

```bash
docker compose --profile test down --remove-orphans
```

---

## 10. Swagger / OpenAPI

Swagger доступен после запуска сервера:

```text
http://localhost:8000/docs
```

ReDoc:

```text
http://localhost:8000/redoc
```

OpenAPI JSON:

```text
http://localhost:8000/openapi.json
```

Основные endpoint-ы:

```text
GET  /health
POST /api/v1/queue/analyze
GET  /api/v1/queue/formulas
```

---

## 11. Частые проблемы

### Web-клиент не может обратиться к API

Проверить `VITE_API_BASE_URL`.

Для локального Vite:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

Для Docker/nginx:

```env
VITE_API_BASE_URL=/api/v1
```

Также проверить CORS на сервере.

Для разработки:

```env
APP_ENV=development
```

### Desktop-клиент не может обратиться к API

Проверить:

```env
API_BASE_URL=http://localhost:8000/api/v1
```

И убедиться, что сервер запущен.

CORS для desktop-клиента не нужен, потому что desktop использует Python `httpx`, а не браузер.

### Docker images из GHCR не скачиваются

Проверить:

```text
GHCR_IMAGE_PREFIX
APP_VERSION
публичность packages в GitHub
```

Если package приватный, нужно авторизоваться:

```bash
docker login ghcr.io
```

### Desktop GUI не запускается в Docker

Это нормально. Docker для `client-desktop` используется только для тестов в headless/offscreen-режиме.

GUI-запуск:

```bash
cd client-desktop
python -m app.main
```

или через собранный `.exe`.

