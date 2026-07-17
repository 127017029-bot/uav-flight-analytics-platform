FROM python:3.11-slim

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements/ requirements/

# Install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements/production.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["sh", "-c", "set -x && echo PORT=$PORT && which daphne && daphne --version && python manage.py migrate --noinput && echo 'Launching Daphne...' && daphne -b 0.0.0.0 -p $PORT config.asgi:application"]
