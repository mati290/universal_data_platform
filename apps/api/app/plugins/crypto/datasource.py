from __future__ import annotations

from app.plugins.base import DataSource
from app.plugins.crypto.extractor import CryptoExtractor
from app.plugins.crypto.transformer import CryptoTransformer


class CryptoDataSource(DataSource):
    source_type = "crypto"

    def __init__(self) -> None:
        super().__init__(extractor=CryptoExtractor(), transformer=CryptoTransformer())
