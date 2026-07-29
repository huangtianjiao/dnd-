# Stage 1: Build frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/ui
COPY ui/package.json ui/package-lock.json* ./
RUN npm ci --production=false
COPY ui/ ./
RUN npm run build

# Stage 2: Production
FROM python:3.12-slim AS production
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY data/ ./data/

# Copy built frontend
COPY --from=frontend-builder /app/ui/out/ ./ui/out/

# Create non-root user
RUN useradd -m -u 1000 aidm
USER aidm

# Environment variables
ENV AIDM_PROJECT_ROOT=/app
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Start command
CMD ["uvicorn", "aidm.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
