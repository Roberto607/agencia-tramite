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
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py collectstatic --noinput && python manage.py bootstrap_superuser && gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000}"]
