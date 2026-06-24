"""
FastAPI application for the SmartMemory Supervision Dashboard.

This API provides endpoints for monitoring and administering the SmartMemory
Semantic Memory system, including statistics, facts exploration, rule management,
and inference control.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import asyncio
import json
import uuid
import anyio
from sse_starlette.sse import EventSourceResponse
from starlette.requests import Request
from starlette.responses import Response
from mcp.types import JSONRPCMessage

# Initialize MCP Server components
from smart_memory.server import SemanticMemoryServer

app = FastAPI(
    title="SmartMemory Supervision API",
    description="API for supervising the SmartMemory inference engine",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global server instance
mcp_server = SemanticMemoryServer()

# Session storage: session_id -> {"read": SendStream, "task": Task}
sessions = {}

# --- Frontend Configuration ---
# Check if the directory exists to avoid errors during development if frontend isn't built
frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "build")
frontend_built = os.path.exists(frontend_dist)

# --- Startup/Shutdown ---

@app.on_event("startup")
async def startup_event():
    """Initialize the Semantic Memory Server on startup."""
    await mcp_server.startup()
    # Register tools
    mcp_server.register_tools()

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown the Semantic Memory Server."""
    await mcp_server.shutdown()
    # Cancel all active sessions
    for session in sessions.values():
        session["task"].cancel()

# --- MCP Endpoints ---

@app.get("/sse")
async def handle_sse(request: Request):
    """Handle incoming SSE connections for MCP."""
    session_id = str(uuid.uuid4())
    inbound_send, inbound_recv = anyio.create_memory_object_stream(100)
    outbound_send, outbound_recv = anyio.create_memory_object_stream(100)
    
    async def run_session():
        try:
            await mcp_server.server.run(
                inbound_recv,
                outbound_send,
                mcp_server.server.create_initialization_options(),
                raise_exceptions=False
            )
        except Exception as e:
            print(f"Session {session_id} error: {e}")
        finally:
            await outbound_send.aclose()

    task = asyncio.create_task(run_session())
    sessions[session_id] = {"inbound": inbound_send, "task": task}
    
    async def event_generator():
        endpoint = f"/api/messages?session_id={session_id}"
        yield {"event": "endpoint", "data": endpoint}
        
        try:
            async with outbound_recv:
                async for message in outbound_recv:
                    if hasattr(message, "model_dump_json"):
                         data = message.model_dump_json()
                    else:
                         data = json.dumps(message)
                    yield {"event": "message", "data": data}
        except asyncio.CancelledError:
            pass
        finally:
            if session_id in sessions:
                del sessions[session_id]
            task.cancel()

    return EventSourceResponse(event_generator())

@app.post("/messages")
async def handle_messages(request: Request):
    """Handle incoming messages from MCP client."""
    session_id = request.query_params.get("session_id")
    if not session_id or session_id not in sessions:
        return Response("Session not found", status_code=404)
    
    try:
        body = await request.json()
        message = JSONRPCMessage.validate_python(body)
        await sessions[session_id]["inbound"].send(message)
        return Response("Accepted", status_code=202)
    except Exception as e:
        return Response(f"Error: {str(e)}", status_code=400)

# --- API Endpoints ---

# Health
@app.get("/health")
async def health():
    """Detailed health check endpoint."""
    return {"status": "healthy", "api": "running"}

# Routers
from api.endpoints import stats, facts, rules, inference, admin, documents, bulk_validation, llm_config

app.include_router(stats.router, prefix="/api", tags=["stats"])
app.include_router(facts.router, prefix="/api", tags=["facts"])
app.include_router(rules.router, prefix="/api", tags=["rules"])
app.include_router(inference.router, prefix="/api", tags=["inference"])
app.include_router(admin.router, prefix="/api", tags=["admin"])
app.include_router(documents.router, prefix="/api", tags=["documents"])
app.include_router(bulk_validation.router, prefix="/api", tags=["validation"])
app.include_router(llm_config.router, prefix="/api", tags=["llm"])

# --- Frontend Serving ---

@app.get("/")
async def root():
    """Serve the dashboard."""
    if frontend_built:
        return FileResponse(os.path.join(frontend_dist, "index.html"))
    return {
        "status": "ok", 
        "service": "SmartMemory Supervision API", 
        "message": "Dashboard not built/found."
    }

if frontend_built:
    app.mount("/_app", StaticFiles(directory=os.path.join(frontend_dist, "_app")), name="_app")
    
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("api"):
            return {"error": "Not Found", "status": 404}
        
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
             return FileResponse(file_path)

        return FileResponse(os.path.join(frontend_dist, "index.html"))
