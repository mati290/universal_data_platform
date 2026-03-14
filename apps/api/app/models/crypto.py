from datetime import datetime

from pydantic import BaseModel


class CryptoLiveLatestRow(BaseModel):
    source_name: str
    symbol: str
    asset_id: str | None = None
    price_usd: float
    event_time: datetime
    provider: str | None = None


class CryptoArchiveLatestRow(BaseModel):
    source_file: str
    coin_name: str
    symbol: str
    event_time: datetime
    high: float
    low: float
    open: float
    close: float
    volume: float
    marketcap: float


class CryptoLiveLatestResponse(BaseModel):
    total_rows: int
    rows: list[CryptoLiveLatestRow]


class CryptoArchiveLatestResponse(BaseModel):
    total_rows: int
    rows: list[CryptoArchiveLatestRow]