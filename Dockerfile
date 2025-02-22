FROM python:3.12.5-slim

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 - 

ENV PATH="/root/.local/bin:${PATH}"
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --only main

COPY . .
RUN mkdir -p /var/log/talatrivia

EXPOSE 8000

CMD ["sh", "-c", "poetry run python manage.py migrate && \
                  poetry run python manage.py collectstatic --noinput && \
                  poetry run gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 30 --access-logfile - --error-logfile -"]
