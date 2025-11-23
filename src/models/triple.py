from pydantic import BaseModel

class Triple(BaseModel):
    subject: str
    predicate: str
    object: str

    def __str__(self):
        return f"({self.subject}, {self.predicate}, {self.object})"
