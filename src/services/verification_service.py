from typing import List
from src.models.verification_request import VerificationRequest

class VerificationService:
    def __init__(self):
        # For now, we'll just store pending verifications in a list.
        # In a real application, this would be a database.
        self.pending_verifications: List[VerificationRequest] = []

    def add(self, verification_request: VerificationRequest):
        self.pending_verifications.append(verification_request)

    def get_pending(self) -> List[VerificationRequest]:
        return self.pending_verifications

    def resolve(self, verification_id: str, approved: bool):
        self.pending_verifications = [
            v for v in self.pending_verifications if v.id != verification_id
        ]
