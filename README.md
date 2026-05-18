# Queue Analysis Server Setup

Архив содержит стартовую настройку FastAPI-сервера с `.env`, конфигурационным модулем и Docker-запуском.

## Локальный запуск

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

Установка зависимостей:

```bash
pip install -r requirements.txt
```

Запуск:

```bash
uvicorn app.main:app --reload
```

Проверка:

- http://localhost:8000/health
- http://localhost:8000/docs
- http://localhost:8000/api/v1/queue/default

## Docker-запуск

Из корня проекта:

```bash
docker compose up --build
```

Остановка:

```bash
docker compose down
```

## Важно

Файл `server/.env` добавлен для удобного локального запуска. В Git обычно коммитят только `server/.env.example`, а `server/.env` оставляют локальным.
