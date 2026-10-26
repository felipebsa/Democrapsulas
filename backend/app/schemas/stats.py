from pydantic import BaseModel

class SchemaStats(BaseModel):
    users: int
    capsules: int
    open_capsules: int
    waiting_capsules: int
    capsules_per_hall: dict[str, int]
    votes: int
