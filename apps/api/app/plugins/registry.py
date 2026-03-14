from __future__ import annotations

from app.plugins.base import DataSource
from app.plugins.crypto.datasource import CryptoDataSource
from app.plugins.transport.datasource import TransportDataSource
from app.plugins.weather.datasource import WeatherDataSource

_PLUGIN_MAP: dict[str, type[DataSource]] = {
    "crypto": CryptoDataSource,
    "weather": WeatherDataSource,
    "transport": TransportDataSource,
}


def get_data_source_plugin(source_type: str) -> DataSource:
    key = source_type.strip().lower()
    plugin_cls = _PLUGIN_MAP.get(key)
    if plugin_cls is None:
        supported = ", ".join(sorted(_PLUGIN_MAP.keys()))
        raise ValueError(f"Unsupported source type '{source_type}'. Supported types: {supported}")
    return plugin_cls()


def supported_source_types() -> list[str]:
    return sorted(_PLUGIN_MAP.keys())
