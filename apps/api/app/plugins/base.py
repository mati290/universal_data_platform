from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import pandas as pd


class DataExtractor(ABC):
    @abstractmethod
    def extract(self, raw_records: list[dict[str, Any]]) -> pd.DataFrame:
        raise NotImplementedError


class DataTransformer(ABC):
    @abstractmethod
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError


class DataSource(ABC):
    source_type: str

    def __init__(self, extractor: DataExtractor, transformer: DataTransformer) -> None:
        self.extractor = extractor
        self.transformer = transformer

    def extract(self, raw_records: list[dict[str, Any]]) -> pd.DataFrame:
        return self.extractor.extract(raw_records)

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        return self.transformer.transform(df)

    def run(self, raw_records: list[dict[str, Any]]) -> pd.DataFrame:
        extracted = self.extract(raw_records)
        return self.transform(extracted)
