# Stage 1: Export dependencies
FROM python:3.12-slim AS builder

WORKDIR /build

RUN pip install --no-cache-dir poetry==1.8.0

COPY pyproject.toml poetry.lock* ./

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# Stage 2: Production image
FROM python:3.12-slim

RUN useradd -m -u 1000 etluser

WORKDIR /app

COPY --from=builder /build/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY resources/ ./resources/

RUN chown -R etluser:etluser /app

USER etluser

ENTRYPOINT ["python", "src/pipeline.py"]
