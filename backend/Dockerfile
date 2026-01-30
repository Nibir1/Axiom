# backend/Dockerfile

# Stage 1: Builder
FROM python:3.11-slim AS builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc

# Install Poetry and the export plugin (REQUIRED for 'poetry export')
RUN pip install poetry poetry-plugin-export

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Export dependencies INCLUDING dev dependencies (pytest, httpx)
RUN poetry export --with dev -f requirements.txt --output requirements.txt --without-hashes

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from builder
COPY --from=builder /app/requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Download Spacy Model
RUN python -m spacy download en_core_web_sm

# Copy Application Code
COPY . .

# Expose Port
EXPOSE 8000

# Run Application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]