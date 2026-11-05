# Stage 1: Build React Frontend
FROM node:20-slim AS frontend-builder
WORKDIR /app/dashboard
COPY dashboard/package*.json ./
RUN npm install
COPY dashboard/ ./
RUN npm run build

# Stage 2: Python Backend Runtime
FROM python:3.11-slim
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MPLCONFIGDIR=/tmp/mpl \
    PORT=8000

# Install minimal OS dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy configuration and source files
COPY pyproject.toml README.md ./
COPY src/ ./src/
COPY experiments/aggregated/ ./experiments/aggregated/

# Install python package and dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# Copy built frontend assets from stage 1
COPY --from=frontend-builder /app/dashboard/dist ./dashboard/dist

EXPOSE 8000

# Run uvicorn binding to 0.0.0.0 and Render's dynamic $PORT
CMD ["sh", "-c", "uvicorn agqca.api.server:app --host 0.0.0.0 --port ${PORT:-8000}"]

