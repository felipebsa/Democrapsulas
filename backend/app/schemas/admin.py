from datetime import datetime
from pydantic import BaseModel

#admins always see the full capsule, plus its reports
class SchemaAdminCapsule(BaseModel):
    id: int
    hall: str
    title: str
    content: str
    author: str
    is_private: bool
    is_hidden: bool
    open_at: datetime
    created: datetime
    reports: int
    reasons: list[str]
