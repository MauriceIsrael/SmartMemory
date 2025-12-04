"""
Rules endpoint for the supervision API.
Provides access to inference rules and allows toggling their state.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from services.memory_service import get_memory_service


router = APIRouter()


class InferenceRule(BaseModel):
    """Inference rule model."""
    id: str
    description: str
    sparql_query: str
    is_active: bool
    execution_count: int
    triples_generated: int
    validation_error: Optional[str] = None
    source: str = "default"  # 'default' | 'custom' | 'dynamic'


@router.get("/rules", response_model=List[InferenceRule])
async def get_rules(
    source: Optional[str] = Query(
        None,
        description="Filter rules by source: 'default' for built-in rules, 'dynamic' for dynamically loaded rules"
    )
):
    """
    Get all inference rules with their metadata.
    
    Args:
        source: Optional filter for rule source ('default' or 'dynamic')
    
    Returns:
        List of all inference rules with statistics, optionally filtered
    """
    memory_service = get_memory_service()
    rules = memory_service.get_rules(source=source)
    return [InferenceRule(**rule) for rule in rules]


@router.post("/rules/{rule_id}/toggle", response_model=InferenceRule)
async def toggle_rule(rule_id: str):
    """
    Toggle an inference rule's active state.
    
    Args:
        rule_id: ID of the rule to toggle
    
    Returns:
        Updated rule with new state
    
    Raises:
        HTTPException: If rule not found
    """
    memory_service = get_memory_service()
    updated_rule = memory_service.toggle_rule(rule_id)
    
    if updated_rule is None:
        raise HTTPException(status_code=404, detail=f"Rule '{rule_id}' not found")
    
    return InferenceRule(**updated_rule)
