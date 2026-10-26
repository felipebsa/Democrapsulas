from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from app.core.constants import USERNAME_MAX_LENGTH

class SchemaUserCreate(BaseModel):
    name: str = Field(min_length=3, max_length=USERNAME_MAX_LENGTH, pattern=r"^[A-Za-z0-9_]+$")
    password: str = Field(min_length=6, max_length=128)

class SchemaUserResponse(BaseModel):
    id: int
    name: str
    created: datetime

    model_config = ConfigDict(from_attributes=True)
