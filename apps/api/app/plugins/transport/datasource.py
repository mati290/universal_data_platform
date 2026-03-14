from __future__ import annotations

from app.plugins.base import DataSource
from app.plugins.transport.extractor import TransportExtractor
from app.plugins.transport.transformer import TransportTransformer


class TransportDataSource(DataSource):
    source_type = "transport"

    def __init__(self) -> None:
        super().__init__(extractor=TransportExtractor(), transformer=TransportTransformer())
