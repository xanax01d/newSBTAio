FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml README.md alembic.ini ./
COPY src ./src
COPY alembic ./alembic
COPY pictures ./pictures

RUN pip install --upgrade pip && pip install .

CMD ["sh", "-c", "alembic upgrade head && sbt-bot"]
