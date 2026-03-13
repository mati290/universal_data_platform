from datetime import datetime

from pydantic import BaseModel, Field


class SourceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    type: str = Field(min_length=1, max_length=60)
    description: str | None = Field(default=None, max_length=500)


class SourceRead(BaseModel):
    id: str
    name: str
    type: str
    description: str | None = None
    created_at: datetime
