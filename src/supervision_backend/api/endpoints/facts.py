"""
Facts endpoint for the supervision API.
Provides access to facts in the knowledge graph with pagination and search.
"""

from typing import List, Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel

from services.memory_service import get_memory_service


router = APIRouter()


class Fact(BaseModel):
    """Fact (triplet) model."""
    Subject: str
    Predicate: str
    Object: str
    Provenance: str


class FactsResponse(BaseModel):
    """Response model for facts list."""
    total_items: int
    items: List[Fact]


@router.get("/facts", response_model=FactsResponse)
async def get_facts(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(50, ge=1, le=500, description="Items per page"),
    search: Optional[str] = Query(None, description="Search term to filter facts"),
    origin: Optional[str] = Query(
        None,
        description="Filter facts by origin: 'explicit' for stated facts, 'inferred' for derived facts"
    ),
    auto_reload: bool = Query(True, description="Auto-reload graph from disk before fetching facts")
):
    """
    Get paginated list of facts from the knowledge graph.
    
    By default, auto-reloads the graph from disk to show current data.
    
    Args:
        page: Page number (starts at 1)
        page_size: Number of items per page (max 500)
        search: Optional search term to filter by subject, predicate, or object
        origin: Optional filter for fact origin ('explicit' or 'inferred')
        auto_reload: If True (default), reload graph before fetching facts
    
    Returns:
        Paginated list of facts with total count, optionally filtered
    """
    memory_service = get_memory_service()
    
    # Auto-reload to get fresh data
    if auto_reload:
        memory_service.reload_graph()
    
    facts, total_count = memory_service.get_facts(
        page=page,
        page_size=page_size,
        search=search,
        origin=origin
    )
    
    return FactsResponse(
        total_items=total_count,
        items=[Fact(**fact) for fact in facts]
    )
