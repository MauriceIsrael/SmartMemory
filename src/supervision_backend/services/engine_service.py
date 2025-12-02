"""
Engine Service
Manages the state of inference engines and persists it to engine_state.json.
"""

import json
import os
from pathlib import Path
from typing import Dict

from models.admin import InferenceEngineState, InferenceEngines


# Path to the engine state configuration file
STATE_FILE_PATH = Path(__file__).parent.parent / "engine_state.json"


class EngineService:
    """Service for managing inference engine states."""
    
    def __init__(self, state_file: Path = STATE_FILE_PATH):
        """
        Initialize the engine service.
        
        Args:
            state_file: Path to the JSON file storing engine states
        """
        self.state_file = state_file
        self._ensure_state_file_exists()
    
    def _ensure_state_file_exists(self) -> None:
        """Create the state file with default values if it doesn't exist."""
        if not self.state_file.exists():
            default_state = {
                "owl_reasoning": {
                    "enabled": False,
                    "name": "OWL-RL Engine",
                    "rules_loaded": False
                },
                "sparql_rules": {
                    "enabled": False,
                    "name": "SPARQL Engine",
                    "rules_loaded": False
                }
            }
            self._write_state(default_state)
    
    def _read_state(self) -> Dict:
        """Read the current state from the JSON file."""
        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            # If file is corrupted or missing, recreate it
            self._ensure_state_file_exists()
            with open(self.state_file, 'r') as f:
                return json.load(f)
    
    def _write_state(self, state: Dict) -> None:
        """Write the state to the JSON file."""
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def get_all_engines(self) -> InferenceEngines:
        """
        Get the current state of all inference engines.
        
        Returns:
            InferenceEngines model with current state
        """
        state = self._read_state()
        return InferenceEngines(**state)
    
    def get_engine(self, engine_name: str) -> InferenceEngineState:
        """
        Get the state of a specific engine.
        
        Args:
            engine_name: Name of the engine ('owl_reasoning' or 'sparql_rules')
            
        Returns:
            InferenceEngineState for the requested engine
            
        Raises:
            ValueError: If engine_name is not recognized
        """
        state = self._read_state()
        if engine_name not in state:
            raise ValueError(f"Unknown engine: {engine_name}")
        return InferenceEngineState(**state[engine_name])
    
    def update_engine(self, engine_name: str, enabled: bool) -> InferenceEngineState:
        """
        Update the enabled state of an inference engine.
        
        Args:
            engine_name: Name of the engine to update
            enabled: New enabled state
            
        Returns:
            Updated InferenceEngineState
            
        Raises:
            ValueError: If engine_name is not recognized
        """
        state = self._read_state()
        
        if engine_name not in state:
            raise ValueError(f"Unknown engine: {engine_name}")
        
        # Update the enabled state
        state[engine_name]["enabled"] = enabled
        
        # Update rules_loaded based on enabled state
        # When disabling, unload rules; when enabling, load rules
        state[engine_name]["rules_loaded"] = enabled
        
        # Persist the updated state
        self._write_state(state)
        
        return InferenceEngineState(**state[engine_name])


# Singleton instance
_engine_service_instance: EngineService | None = None


def get_engine_service() -> EngineService:
    """
    Get the singleton instance of EngineService.
    
    Returns:
        EngineService instance
    """
    global _engine_service_instance
    if _engine_service_instance is None:
        _engine_service_instance = EngineService()
    return _engine_service_instance
