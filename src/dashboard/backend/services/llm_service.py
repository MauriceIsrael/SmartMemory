"""
LLM Configuration Service for SmartMemory Dashboard.

Manages LLM provider configuration including API keys, Ollama settings, etc.
"""

import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

from smart_memory.config import config

logger = logging.getLogger(__name__)


class LLMConfig(BaseModel):
    """LLM Configuration model."""
    provider: str = Field(..., description="LLM provider: 'openai', 'anthropic', 'google', or 'ollama'")
    api_key: Optional[str] = Field(None, description="API key for cloud providers")
    model: str = Field(..., description="Model name to use")
    base_url: Optional[str] = Field(None, description="Base URL for Ollama or custom endpoints")
    temperature: float = Field(default=0.7, description="Temperature for LLM responses")


class LLMService:
    """Service for managing LLM configuration."""
    
    def __init__(self, config_file: Optional[Path] = None):
        """Initialize LLM service."""
        self.config_file = config_file or (config.project_root / "llm_config.json")
    
    def get_config(self) -> Optional[LLMConfig]:
        """Get current LLM configuration."""
        if not self.config_file.exists():
            logger.info("No LLM configuration file found")
            return None
        
        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
            return LLMConfig(**data)
        except Exception as e:
            logger.error(f"Error reading LLM config: {e}")
            return None
    
    def get_config_safe(self) -> Optional[Dict[str, Any]]:
        """Get config without exposing full API key."""
        cfg = self.get_config()
        if not cfg:
            return None
        
        data = cfg.model_dump()
        # Mask API key
        if data.get('api_key'):
            key = data['api_key']
            if len(key) > 8:
                data['api_key'] = key[:4] + '****' + key[-4:]
            else:
                data['api_key'] = '****'
        
        return data
    
    def save_config(self, config_data: LLMConfig) -> bool:
        """Save LLM configuration."""
        try:
            # Ensure directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                json.dump(config_data.model_dump(), f, indent=2)
            
            logger.info(f"LLM configuration saved: provider={config_data.provider}, model={config_data.model}")
            return True
        except Exception as e:
            logger.error(f"Error saving LLM config: {e}")
            return False
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test LLM connection with current configuration."""
        cfg = self.get_config()
        if not cfg:
            return {
                "success": False,
                "error": "No LLM configuration found"
            }
        
        try:
            # Import litellm for testing
            import litellm
            
            # Prepare kwargs based on provider
            kwargs = {
                "model": cfg.model,
                "messages": [{"role": "user", "content": "Hello! Please respond with 'OK' if you can read this."}],
                "temperature": cfg.temperature,
                "max_tokens": 10
            }
            
            if cfg.provider == "ollama":
                if cfg.base_url:
                    kwargs["api_base"] = cfg.base_url
                kwargs["model"] = f"ollama/{cfg.model}"
            elif cfg.api_key:
                kwargs["api_key"] = cfg.api_key
            
            # Make test call
            response = await litellm.acompletion(**kwargs)
            
            return {
                "success": True,
                "message": "LLM connection successful",
                "response": response.choices[0].message.content if response.choices else "No response"
            }
            
        except Exception as e:
            logger.error(f"LLM connection test failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Global instance
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get or create global LLM service instance."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
