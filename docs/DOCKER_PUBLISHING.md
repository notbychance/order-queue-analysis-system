# Docker publishing to GHCR

Проект публикует runtime Docker images в GitHub Container Registry.

Публикуются только:

```text
server
client-web
```

`client-desktop` не публикуется как Docker image для GUI-запуска. Desktop распространяется как Windows EXE через release workflow.

## Workflow

Файл:

```text
.github/workflows/docker-publish.yml
```

Workflow запускается:

```text
1. Автоматически при push тега v*.*.*
2. Вручную через workflow_dispatch
```

## Images

Workflow публикует:

```text
ghcr.io/<owner>/<repository>/queue-analysis-server:<tag>
ghcr.io/<owner>/<repository>/queue-analysis-web:<tag>
```

Дополнительно публикуются:

```text
latest
sha-<commit-sha>
```

если включен `push_latest`.

## Required permissions

В workflow уже указано:

```yaml
permissions:
  contents: read
  packages: write
```

Этого достаточно для публикации в GHCR через `GITHUB_TOKEN`.

## Publish by Git tag

Создать тег:

```bash
git tag v1.0.0
git push origin v1.0.0
```

После успешного workflow появятся образы:

```text
ghcr.io/<owner>/<repository>/queue-analysis-server:v1.0.0
ghcr.io/<owner>/<repository>/queue-analysis-web:v1.0.0
```

## Manual publish

GitHub UI:

```text
Actions → Docker Publish → Run workflow
```

Inputs:

```text
image_tag: v1.0.0
push_latest: true
```

## Run published images

Скопируй пример env:

```bash
cp .env.prod.example .env.prod
```

Windows PowerShell:

```powershell
Copy-Item .env.prod.example .env.prod
```

Отредактируй:

```env
GHCR_IMAGE_PREFIX=ghcr.io/<owner>/<repository>
APP_VERSION=v1.0.0
```

Запуск:

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d
```

Проверка:

```text
Web:     http://localhost:8080
FastAPI: http://localhost:8000
Swagger: http://localhost:8000/docs
```

Остановка:

```bash
docker compose -f docker-compose.prod.yml down
```

## Package visibility

GHCR package can be private by default.

If another user cannot pull images, open GitHub package settings and make the package public or give access to the repository/users.

## Local smoke test after publishing

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml pull
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d
```

Then open web UI and run a calculation:

```text
λ = 6
μ = 8
```

Expected result:

```text
utilization = 75%
L = 3
Wq = 9 h
W = 12 h
```

## Difference from development compose

Development compose:

```bash
docker compose up --build
```

builds images locally from source.

Production compose:

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d
```

pulls already published images from GHCR.
