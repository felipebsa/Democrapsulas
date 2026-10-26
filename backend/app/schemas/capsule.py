from datetime import datetime
from pydantic import AwareDatetime, BaseModel, ConfigDict, Field
from app.core.constants import Hall, TITLE_MAX_LENGTH, CONTENT_MAX_LENGTH

class SchemaCapsuleCreate(BaseModel):
    hall: Hall
    title: str = Field(min_length=1, max_length=TITLE_MAX_LENGTH)
    content: str = Field(min_length=1, max_length=CONTENT_MAX_LENGTH)
    is_private: bool = False
    open_at: AwareDatetime

    model_config = ConfigDict(str_strip_whitespace=True)


#title, content and author only come filled after open_at (or for the owner)
class SchemaCapsuleResponse(BaseModel):
    id: int
    hall: str
    is_private: bool
    is_open: bool
    is_mine: bool
    open_at: datetime
    created: datetime
    title: str | None
    content: str | None
    author: str | None
