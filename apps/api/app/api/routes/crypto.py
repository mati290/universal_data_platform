from fastapi import APIRouter, Query

from app.models.crypto import (
    CryptoArchiveLatestResponse,
    CryptoLiveLatestResponse,
)
from app.services.crypto_query_service import crypto_query_service

router = APIRouter(prefix="/crypto", tags=["crypto"])


@router.get("/live/latest", response_model=CryptoLiveLatestResponse)
def get_live_latest(
    limit: int = Query(default=100, ge=1, le=1_000),
    symbol: str | None = Query(default=None, min_length=1, max_length=20),
) -> CryptoLiveLatestResponse:
    normalized_symbol = symbol.strip().upper() if symbol else None
    rows = crypto_query_service.fetch_live_latest(limit=limit, symbol=normalized_symbol)
    return CryptoLiveLatestResponse(total_rows=len(rows), rows=rows)


@router.get("/archive/latest", response_model=CryptoArchiveLatestResponse)
def get_archive_latest(
    limit: int = Query(default=100, ge=1, le=1_000),
    symbol: str | None = Query(default=None, min_length=1, max_length=20),
) -> CryptoArchiveLatestResponse:
    normalized_symbol = symbol.strip().upper() if symbol else None
    rows = crypto_query_service.fetch_archive_latest(limit=limit, symbol=normalized_symbol)
    return CryptoArchiveLatestResponse(total_rows=len(rows), rows=rows)