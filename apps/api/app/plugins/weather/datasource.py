from __future__ import annotations

from app.plugins.base import DataSource
from app.plugins.weather.extractor import WeatherExtractor
from app.plugins.weather.transformer import WeatherTransformer


class WeatherDataSource(DataSource):
    source_type = "weather"

    def __init__(self) -> None:
        super().__init__(extractor=WeatherExtractor(), transformer=WeatherTransformer())
