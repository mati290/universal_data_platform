from __future__ import annotations

import pandas as pd

from app.plugins.base import DataTransformer


class CryptoTransformer(DataTransformer):
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df.copy()

        cleaned = df.copy()

        if "symbol" in cleaned.columns:
            cleaned["symbol"] = cleaned["symbol"].astype(str).str.upper().str.strip()

        if "price_usd" in cleaned.columns:
            cleaned["price_usd"] = pd.to_numeric(cleaned["price_usd"], errors="coerce")

        if "event_time" in cleaned.columns:
            cleaned["event_time"] = pd.to_datetime(cleaned["event_time"], errors="coerce", utc=True, format="ISO8601")

        cleaned = cleaned.replace(r"^\s*$", pd.NA, regex=True)
        cleaned = cleaned.dropna(how="any").drop_duplicates().reset_index(drop=True)
        return cleaned
