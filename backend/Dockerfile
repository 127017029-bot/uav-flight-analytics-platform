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

CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn config.asgi:application --worker-class uvicorn.workers.UvicornWorker --workers 1 --bind 0.0.0.0:$PORT --log-level debug --error-logfile - --access-logfile -"]
