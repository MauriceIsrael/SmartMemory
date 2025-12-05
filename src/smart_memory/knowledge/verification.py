from dataclasses import dataclass, field
from datetime import datetime
import uuid

@dataclass
class VerificationRequest:
    triple: tuple
    confidence: float
    source_rule: str
    context: dict
    id: str = field(default_factory=lambda: f"ver_{uuid.uuid4()}")
    created_at: datetime = field(default_factory=datetime.utcnow)
    status: str = "pending"
