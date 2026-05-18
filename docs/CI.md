# CI

В проекте настроен CI через GitHub Actions.

Файл workflow:

```text
.github/workflows/ci.yml
```

## Когда запускается

CI запускается при:

```text
push      в main / master / develop
pull_request в main / master / develop
manual run через workflow_dispatch
```

## Jobs

### Server tests

Рабочая директория:

```text
server/
```

Действия:

```text
1. Установка Python 3.12.
2. Установка server/requirements-dev.txt.
3. Запуск pytest.
```

Проверяется:

```text
- unit-тесты расчетного сервиса;
- FastAPI endpoint-ы;
- CORS;
- Swagger/OpenAPI;
- интеграционные контрактные тесты.
```

Локальный аналог:

```bash
cd server
pip install -r requirements-dev.txt
pytest
```

---

### Web tests and build

Рабочая директория:

```text
client-web/
```

Действия:

```text
1. Установка Node.js 22.
2. npm ci.
3. npm run test:unit -- --run.
4. npm run type-check.
5. npm run build.
```

Локальный аналог:

```bash
cd client-web
npm ci
npm run test:unit -- --run
npm run type-check
npm run build
```

---

### Desktop tests

Рабочая директория:

```text
client-desktop/
```

Действия:

```text
1. Установка системных библиотек Qt/PySide6.
2. Установка Python 3.12.
3. Установка client-desktop/requirements-dev.txt.
4. Запуск pytest.
```

Для headless-среды используется:

```env
QT_QPA_PLATFORM=offscreen
```

Локальный аналог:

```bash
cd client-desktop
pip install -r requirements-dev.txt
pytest
```

---

### Docker compose validation

Запускается после успешных тестов всех модулей.

Действия:

```text
1. docker compose config
2. docker compose build server client-web
```

Этот job проверяет, что основной Docker Compose корректно собирает runtime-сервисы.

## Почему в CI не запускается desktop GUI

Desktop-клиент использует PySide6/QML и требует графическое окружение.

В CI проверяются:

```text
- Python-код;
- ViewModel;
- API-клиент;
- SQLite/SQLAlchemy;
- сервисы;
- QML-зависимости через тесты в offscreen-режиме.
```

Полноценный запуск окна выполняется локально:

```bash
cd client-desktop
python -m app.main
```

## Что делать, если CI упал

### Server

Проверить локально:

```bash
cd server
pytest
```

### Web

Проверить локально:

```bash
cd client-web
npm ci
npm run test:unit -- --run
npm run type-check
npm run build
```

### Desktop

Проверить локально:

```bash
cd client-desktop
pytest
```

### Docker

Проверить локально из корня проекта:

```bash
docker compose config
docker compose build server client-web
```
