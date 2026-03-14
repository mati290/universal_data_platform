from __future__ import annotations

from typing import Any

import pandas as pd

from app.plugins.base import DataExtractor


class CryptoExtractor(DataExtractor):
    def extract(self, raw_records: list[dict[str, Any]]) -> pd.DataFrame:
        return pd.DataFrame(raw_records)
