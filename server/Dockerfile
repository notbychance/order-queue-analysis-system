FROM python:3.12-slim AS base

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

COPY requirements.txt ./

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

RUN groupadd --system appuser \
    && useradd --system --gid appuser --home-dir /app appuser \
    && chown -R appuser:appuser /app


FROM base AS test

USER root

COPY requirements-dev.txt ./

RUN pip install -r requirements-dev.txt

COPY app ./app
COPY tests ./tests
COPY pytest.ini ./pytest.ini

RUN chown -R appuser:appuser /app

USER appuser

CMD ["pytest"]


FROM base AS runtime

COPY app ./app

RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
