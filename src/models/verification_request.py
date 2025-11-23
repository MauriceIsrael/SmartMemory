from pydantic import BaseModel
from src.models.triple import Triple

class VerificationRequest(BaseModel):
    id: str
    triple: Triple
    certainty_score: float
