from __future__ import annotations

import pandas as pd

from app.plugins.base import DataTransformer


class WeatherTransformer(DataTransformer):
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df.copy()

        cleaned = df.copy()

        for column in ["temperature", "humidity", "pressure"]:
            if column in cleaned.columns:
                cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")

        if "observed_at" in cleaned.columns:
            cleaned["observed_at"] = pd.to_datetime(cleaned["observed_at"], errors="coerce", utc=True, format="ISO8601")

        cleaned = cleaned.replace(r"^\s*$", pd.NA, regex=True)
        cleaned = cleaned.dropna(how="any").drop_duplicates().reset_index(drop=True)
        return cleaned
