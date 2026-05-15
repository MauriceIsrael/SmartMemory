# Stage 1: Build Frontend
FROM node:22-alpine AS frontend-builder
WORKDIR /app
COPY src/dashboard/frontend/package.json src/dashboard/frontend/package-lock.json ./
RUN npm ci
COPY src/dashboard/frontend .
RUN npm run build

# Stage 2: Build Python Dependencies
FROM python:3.11-slim AS python-builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml .
# Install dependencies into a specific directory to copy later
RUN pip install --user --no-cache-dir .[oxigraph,supervision]

# Stage 3: Final Image
FROM python:3.11-slim
WORKDIR /app

# Only copy what's needed from builder stages
COPY --from=python-builder /root/.local /root/.local
COPY --from=frontend-builder /app/build /app/src/dashboard/backend/static

# Copy application code
COPY src /app/src
COPY pyproject.toml /app/
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# Set environment variables
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app/src:/app
ENV SEMMEM_PERSISTENCE_BACKEND=turtle
ENV SEMMEM_PERSISTENCE_PATH=/app/data/knowledge_graph.ttl

# Create data directory
RUN mkdir -p /app/data

# Expose port (for dashboard mode)
EXPOSE 8080

# Use entrypoint script
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD []

