"""
FastAPI application for the SmartMemory Supervision Dashboard.

This API provides endpoints for monitoring and administering the SmartMemory
Semantic Memory system, including statistics, facts exploration, rule management,
and inference control.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="SmartMemory Supervision API",
    description="API for supervising the SmartMemory inference engine",
    version="1.0.0",
)

# Configure CORS to allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # SvelteKit dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "SmartMemory Supervision API",
        "version": "1.0.0",
    }


@app.get("/health")
async def health():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "api": "running",
    }


# Import and register endpoint routers
from api.endpoints import stats, facts, rules, inference, admin, documents, bulk_validation

app.include_router(stats.router, prefix="/api", tags=["stats"])
app.include_router(facts.router, prefix="/api", tags=["facts"])
app.include_router(rules.router, prefix="/api", tags=["rules"])
app.include_router(inference.router, prefix="/api", tags=["inference"])
app.include_router(admin.router, prefix="/api", tags=["admin"])
app.include_router(documents.router, prefix="/api", tags=["documents"])
app.include_router(bulk_validation.router, prefix="/api", tags=["validation"])
