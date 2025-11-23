from pydantic import BaseModel
from typing import List
from src.models.triple import Triple

class InferenceRule(BaseModel):
    name: str
    conditions: List[Triple]
    conclusion: Triple
