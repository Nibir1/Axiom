# backend/Dockerfile

# Stage 1: Builder
FROM python:3.11-slim AS builder

WORKDIR /app

# Install system dependencies for build
RUN apt-get update && apt-get install -y gcc

# Install Poetry
RUN pip install poetry

# --- FIX: Install the export plugin (Required for Poetry 2.0+) ---
RUN poetry self add poetry-plugin-export

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Export poetry dependencies to requirements.txt (Standardizes install)
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies (e.g. for Spacy/Numpy)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from builder
COPY --from=builder /app/requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Download Spacy Model (Crucial for Axiom)
RUN python -m spacy download en_core_web_sm

# Copy Application Code
COPY . .

# Expose Port
EXPOSE 8000

# Run Application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]