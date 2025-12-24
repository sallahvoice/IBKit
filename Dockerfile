FROM python:3-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ make libffi-dev libssl-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

WORKDIR /app

COPY . /app

# Create a non-root user
RUN adduser -u 5678 --disabled-password --gecos "" appuser \
    && chown -R appuser /app

USER appuser

CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "backend.api.health:app", "--bind", "0.0.0.0:8000"]
