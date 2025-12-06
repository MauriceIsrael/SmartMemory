"""
LLM Configuration endpoints for the supervision API.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.llm_service import get_llm_service, LLMConfig

router = APIRouter()


class LLMConfigResponse(BaseModel):
    """Response model for LLM config (safe, with masked API key)."""
    provider: str
    api_key: Optional[str]
    model: str
    base_url: Optional[str]
    temperature: float


class TestResponse(BaseModel):
    """Response model for test endpoint."""
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None
    response: Optional[str] = None


@router.get("/llm-config")
async def get_llm_config():
    """Get current LLM configuration (API key masked)."""
    service = get_llm_service()
    config = service.get_config_safe()
    
    if not config:
        return {
            "configured": False,
            "config": None
        }
    
    return {
        "configured": True,
        "config": config
    }


@router.post("/llm-config")
async def save_llm_config(config: LLMConfig):
    """Save LLM configuration."""
    service = get_llm_service()
    success = service.save_config(config)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to save configuration")
    
    return {"success": True, "message": "Configuration saved"}


@router.post("/llm-config/test", response_model=TestResponse)
async def test_llm_config():
    """Test current LLM configuration."""
    service = get_llm_service()
    result = await service.test_connection()
    
    return TestResponse(**result)
