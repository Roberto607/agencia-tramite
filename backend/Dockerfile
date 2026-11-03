FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && groupadd --system django \
    && useradd --system --gid django --create-home django \
    && mkdir -p /app/media \
    && chown -R django:django /app

COPY --chown=django:django . .

USER django
EXPOSE 8000
