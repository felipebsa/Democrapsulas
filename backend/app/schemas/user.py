from pydantic import BaseModel, ConfigDict
from datetime import datetime

class SchemaUserCreate(BaseModel):
    name: str
    password: str

class SchemaUserResponse(BaseModel):
    id: int
    name: str
    created: datetime

    model_config = ConfigDict(from_attributes=True)