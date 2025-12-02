"""
Pydantic models for the admin API.
Defines data structures for inference engine management.
"""

from pydantic import BaseModel, Field


class InferenceEngineState(BaseModel):
    """State of a single inference engine."""
    
    enabled: bool = Field(
        ...,
        description="Whether the engine is currently enabled"
    )
    name: str = Field(
        ...,
        description="Human-readable name of the engine"
    )
    rules_loaded: bool = Field(
        default=False,
        description="Whether the engine's rules are currently loaded"
    )


class InferenceEngines(BaseModel):
    """State of all inference engines in the system."""
    
    owl_reasoning: InferenceEngineState = Field(
        ...,
        description="OWL-RL reasoning engine state"
    )
    sparql_rules: InferenceEngineState = Field(
        ...,
        description="SPARQL rules engine state"
    )


class UpdateEngineRequest(BaseModel):
    """Request body for updating an engine's state."""
    
    enabled: bool = Field(
        ...,
        description="New enabled state for the engine"
    )
