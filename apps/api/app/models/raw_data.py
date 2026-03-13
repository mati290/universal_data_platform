from typing import Any

from pydantic import BaseModel, Field


class RawDataIngestRequest(BaseModel):
    source_id: str = Field(min_length=1)
    records: list[dict[str, Any]] = Field(default_factory=list)


class RawDataIngestResponse(BaseModel):
    source_id: str
    records_saved: int
