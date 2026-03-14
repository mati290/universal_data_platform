from __future__ import annotations

import pandas as pd

from app.plugins.base import DataTransformer


NUMERIC_COLUMNS = [
    "price_usd",
    "open_price_usd",
    "min_price_usd_24h",
    "max_price_usd_24h",
    "volume_24h",
    "market_cap_usd",
    "change_pct_24h",
]


class CryptoTransformer(DataTransformer):
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df.copy()

        cleaned = df.copy()

        if "symbol" in cleaned.columns:
            cleaned["symbol"] = cleaned["symbol"].astype("string").str.upper().str.strip()
            cleaned.loc[cleaned["symbol"].isin(["", "NAN", "NONE", "NULL"]), "symbol"] = pd.NA

        if "asset_id" in cleaned.columns:
            cleaned["asset_id"] = cleaned["asset_id"].astype("string").str.lower().str.strip()
            cleaned.loc[cleaned["asset_id"].isin(["", "nan", "none", "null"]), "asset_id"] = pd.NA

        for column in NUMERIC_COLUMNS:
            if column in cleaned.columns:
                cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")

        if "event_time" in cleaned.columns:
            cleaned["event_time"] = pd.to_datetime(cleaned["event_time"], errors="coerce", utc=True, format="ISO8601")

        cleaned = cleaned.replace(r"^\s*$", pd.NA, regex=True)
        cleaned = cleaned.dropna(how="any").drop_duplicates().reset_index(drop=True)

        if "price_usd" in cleaned.columns:
            cleaned = cleaned[cleaned["price_usd"] > 0]

        if "open_price_usd" in cleaned.columns:
            cleaned = cleaned[cleaned["open_price_usd"] > 0]

        if "min_price_usd_24h" in cleaned.columns:
            cleaned = cleaned[cleaned["min_price_usd_24h"] > 0]

        if "max_price_usd_24h" in cleaned.columns:
            cleaned = cleaned[cleaned["max_price_usd_24h"] > 0]

        if "volume_24h" in cleaned.columns:
            cleaned = cleaned[cleaned["volume_24h"] >= 0]

        if "market_cap_usd" in cleaned.columns:
            cleaned = cleaned[cleaned["market_cap_usd"] >= 0]

        if {"min_price_usd_24h", "max_price_usd_24h"}.issubset(cleaned.columns):
            cleaned = cleaned[cleaned["min_price_usd_24h"] <= cleaned["max_price_usd_24h"]]

        if {"price_usd", "min_price_usd_24h", "max_price_usd_24h"}.issubset(cleaned.columns):
            cleaned = cleaned[
                (cleaned["price_usd"] >= cleaned["min_price_usd_24h"])
                & (cleaned["price_usd"] <= cleaned["max_price_usd_24h"])
            ]

        cleaned = cleaned.reset_index(drop=True)
        return cleaned
