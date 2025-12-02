"""
Admin API router for managing inference engines.
Provides endpoints for toggling engines and filtering rules/facts.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from models.admin import (
    InferenceEngineState,
    InferenceEngines,
    UpdateEngineRequest
)
from services.engine_service import get_engine_service


router = APIRouter()


@router.get("/inference-engines", response_model=InferenceEngines)
async def get_inference_engines():
    """
    Get the current state of all inference engines.
    
    Returns:
        Current state of OWL-RL and SPARQL engines
    """
    engine_service = get_engine_service()
    return engine_service.get_all_engines()


@router.post("/inference-engines/{engine_name}", response_model=InferenceEngineState)
async def update_inference_engine(
    engine_name: str,
    request: UpdateEngineRequest
):
    """
    Update the state of a specific inference engine.
    
    Args:
        engine_name: Name of the engine ('owl_reasoning' or 'sparql_rules')
        request: Request body containing the new enabled state
        
    Returns:
        Updated state of the engine
        
    Raises:
        HTTPException: If engine_name is not recognized
    """
    engine_service = get_engine_service()
    
    try:
        updated_engine = engine_service.update_engine(
            engine_name=engine_name,
            enabled=request.enabled
        )
        return updated_engine
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/rules")
async def get_rules(
    source: Optional[str] = Query(
        None,
        description="Filter rules by source: 'default' for built-in, 'dynamic' for loaded"
    )
):
    """
    Get inference rules with optional filtering.
    
    Args:
        source: Optional filter for rule source
        
    Returns:
        List of rules, optionally filtered
        
    Note:
        This is a placeholder implementation. The actual rule filtering
        logic will need to be integrated with the existing rules endpoint.
    """
    # TODO: Integrate with existing rules.py endpoint
    # For now, return a placeholder response
    return {
        "message": "Rules endpoint - to be integrated with existing implementation",
        "filter": source
    }


@router.get("/facts")
async def get_facts(
    origin: Optional[str] = Query(
        None,
        description="Filter facts by origin: 'explicit' for stated, 'inferred' for derived"
    )
):
    """
    Get facts with optional filtering.
    
    Args:
        origin: Optional filter for fact origin
        
    Returns:
        List of facts, optionally filtered
        
    Note:
        This is a placeholder implementation. The actual fact filtering
        logic will need to be integrated with the existing facts endpoint.
    """
    # TODO: Integrate with existing facts.py endpoint
    # For now, return a placeholder response
    return {
        "message": "Facts endpoint - to be integrated with existing implementation",
        "filter": origin
    }
