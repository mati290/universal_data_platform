from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class DataSourceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    source_type: str = Field(min_length=1, max_length=60)
    description: str | None = Field(default=None, max_length=500)


class DataSource(BaseModel):
    id: str
    name: str
    source_type: str
    description: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    rows_count: int = 0


class CsvUploadSummary(BaseModel):
    source_id: str
    rows_loaded: int
    columns: list[str]


class DataRowsResponse(BaseModel):
    source_id: str
    total_rows: int
    rows: list[dict[str, Any]]
