from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

class SchemaUserCreate(BaseModel):
    name: str = Field(min_length=3, max_length=20, pattern=r"^[A-Za-z0-9_]+$")
    password: str = Field(min_length=6, max_length=128)

class SchemaUserResponse(BaseModel):
    id: int
    name: str
    created: datetime

    model_config = ConfigDict(from_attributes=True)
