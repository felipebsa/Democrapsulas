from datetime import datetime
from pydantic import AwareDatetime, BaseModel, ConfigDict

class SchemaCapsuleCreate(BaseModel):
    title: str
    content: str
    is_private: bool
    open_at: AwareDatetime


class SchemaCapsuleResponse(BaseModel):
    id: int
    user_id: int
    title: str
    content: str
    is_private: bool
    open_at: datetime
    created: datetime

    model_config = ConfigDict(from_attributes=True)
