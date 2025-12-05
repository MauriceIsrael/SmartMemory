"""
Stats endpoint for the supervision API.
Provides system statistics about the knowledge graph and inference engine.
"""

from fastapi import APIRouter
from pydantic import BaseModel

from services.memory_service import get_memory_service


router = APIRouter()


class SystemStats(BaseModel):
    """System statistics model."""
    total_triplets: int
    inferred_triplet_count: int
    asserted_triplet_count: int
    active_rule_count: int
    inactive_rule_count: int


@router.get("/stats", response_model=SystemStats)
async def get_stats(auto_reload: bool = True):
    """
    Get system statistics.
    
    By default, this automatically reloads the graph from disk before
    returning statistics, ensuring the dashboard always shows current data
    even when the MCP server has modified the knowledge graph.
    
    Args:
        auto_reload: If True (default), reload graph before returning stats
    
    Returns key metrics about the knowledge graph and rule engine:
    - Total number of triplets in the graph
    - Count of inferred vs. asserted triplets
    - Count of active vs. inactive inference rules
    """
    memory_service = get_memory_service()
    
    # Auto-reload to get fresh data from disk
    if auto_reload:
        memory_service.reload_graph()
    
    stats = memory_service.get_system_stats()
    return SystemStats(**stats)

