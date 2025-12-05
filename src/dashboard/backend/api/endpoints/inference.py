"""
Inference endpoint for the supervision API.
Provides ability to manually trigger inference runs.
"""

from fastapi import APIRouter
from pydantic import BaseModel

from services.memory_service import get_memory_service


router = APIRouter()


class InferenceRunResponse(BaseModel):
    """Response model for inference run."""
    status: str
    message: str
    triples_inferred: int = 0


@router.post("/inference/run", response_model=InferenceRunResponse, status_code=202)
async def run_inference():
    """
    Manually trigger a full inference run.
    
    Returns:
        Status and results of the inference run
    """
    memory_service = get_memory_service()
    result = memory_service.run_inference()
    
    return InferenceRunResponse(
        status=result["status"],
        message=result["message"],
        triples_inferred=result.get("triples_inferred", 0)
    )
