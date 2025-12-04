"""
Admin endpoint for the supervision API.
Provides administrative functions like reloading the graph and system control.
"""

from fastapi import APIRouter
from pydantic import BaseModel

from services.memory_service import get_memory_service


router = APIRouter()


class ReloadResponse(BaseModel):
    """Response model for reload operation."""
    status: str
    message: str
    triple_count: int


@router.post("/admin/reload", response_model=ReloadResponse)
async def reload_graph():
    """
    Reload the knowledge graph from disk.
    
    This endpoint is useful to refresh the dashboard data after the MCP server
    has made changes to the knowledge graph during an LLM conversation.
    
    Returns:
        Status of the reload operation with updated triple count
    """
    memory_service = get_memory_service()
    result = memory_service.reload_graph()
    
    return ReloadResponse(
        status=result["status"],
        message=result["message"],
        triple_count=result["triple_count"]
    )
