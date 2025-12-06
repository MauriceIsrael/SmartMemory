# Build Stage for Frontend
FROM node:22-alpine AS frontend-builder

WORKDIR /app
COPY src/dashboard/frontend/package.json src/dashboard/frontend/package-lock.json ./
RUN npm ci

COPY src/dashboard/frontend .
RUN npm run build

# Final Stage
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies if needed (e.g. for pdf processing)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY src/dashboard/backend/requirements.txt .
# Add project dependencies (from pyproject.toml context - simplifying here for requirements.txt usage)
# In a real scenario we might install the package itself, but here we run from source
RUN pip install --no-cache-dir -r requirements.txt
# RUN pip install --no-cache-dir litellm PyMuPDF requests - Moved to requirements.txt

# Copy application code
COPY src /app/src
COPY pyproject.toml /app/

# Copy built frontend assets to backend static folder
# We rename 'build' to 'static' to match our backend logic
COPY --from=frontend-builder /app/build /app/src/dashboard/backend/static

# Set PYTHONPATH
ENV PYTHONPATH=/app/src:/app:/app/src/dashboard/backend

# Expose port
EXPOSE 8080

# Run the application
CMD ["uvicorn", "src.dashboard.backend.main:app", "--host", "0.0.0.0", "--port", "8080"]
