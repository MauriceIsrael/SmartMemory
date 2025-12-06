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



class PendingRule(BaseModel):
    """Pending rule model."""
    id: str
    description: str
    sparql_pattern: str
    confidence: float
    num_inferences: Optional[int] = None
    preview: Optional[str] = None


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


@router.get("/rules/pending", response_model=List[PendingRule])
async def get_pending_rules(doc_id: Optional[str] = Query(None, description="Filter by Source Document URI or ID")):
    """Get all rules pending approval."""
    memory_service = get_memory_service()
    rules = memory_service.get_pending_rules(doc_id=doc_id)
    
    # Map raw dict to PendingRule model
    # Note: pending rules format in JSON might have different keys than backend model if we aren't careful
    # JSON has: description, sparql_pattern, confidence, ...
    return [PendingRule(**rule) for rule in rules]


@router.post("/rules/pending/{rule_id}/approve")
async def approve_pending_rule(rule_id: str):
    """Approve a pending rule."""
    memory_service = get_memory_service()
    success = memory_service.approve_pending_rule(rule_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Pending rule '{rule_id}' not found or failed to approve")
    return {"status": "approved", "id": rule_id}


@router.post("/rules/pending/{rule_id}/reject")
async def reject_pending_rule(rule_id: str):
    """Reject a pending rule."""
    memory_service = get_memory_service()
    success = memory_service.reject_pending_rule(rule_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Pending rule '{rule_id}' not found")
    return {"status": "rejected", "id": rule_id}


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
