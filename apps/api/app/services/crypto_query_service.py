from __future__ import annotations

from sqlalchemy import text

from app.core.db import SessionLocal


class CryptoQueryService:
    def fetch_live_latest(self, limit: int, symbol: str | None = None) -> list[dict[str, object]]:
        sql = """
            SELECT source_name, symbol, asset_id, price_usd, event_time, provider
            FROM public.crypto_latest
        """
        params: dict[str, object] = {"limit": limit}
        if symbol:
            sql += " WHERE symbol = :symbol"
            params["symbol"] = symbol

        sql += " ORDER BY symbol LIMIT :limit"
        query = text(sql)

        with SessionLocal() as db:
            result = db.execute(query, params)
            return [dict(row._mapping) for row in result]

    def fetch_archive_latest(self, limit: int, symbol: str | None = None) -> list[dict[str, object]]:
        sql = """
            SELECT source_file, coin_name, symbol, event_time, high, low, open, close, volume, marketcap
            FROM public.crypto_csv_latest
        """
        params: dict[str, object] = {"limit": limit}
        if symbol:
            sql += " WHERE symbol = :symbol"
            params["symbol"] = symbol

        sql += " ORDER BY symbol LIMIT :limit"
        query = text(sql)

        with SessionLocal() as db:
            result = db.execute(query, params)
            return [dict(row._mapping) for row in result]


crypto_query_service = CryptoQueryService()