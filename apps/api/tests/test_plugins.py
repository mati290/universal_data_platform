import pandas as pd
import pytest

from app.plugins import get_data_source_plugin, supported_source_types


def test_supported_source_types_contains_expected_plugins() -> None:
    assert supported_source_types() == ["crypto", "transport", "weather"]


@pytest.mark.parametrize("source_type", ["crypto", "weather", "transport"])
def test_registry_returns_plugin_instance(source_type: str) -> None:
    plugin = get_data_source_plugin(source_type)
    assert plugin.source_type == source_type


def test_crypto_plugin_transform() -> None:
    plugin = get_data_source_plugin("crypto")
    frame = pd.DataFrame(
        [
            {"symbol": " btc ", "price_usd": "99123.5", "event_time": "2026-03-13T10:00:00Z"},
            {"symbol": "", "price_usd": "12", "event_time": "2026-03-13T11:00:00Z"},
        ]
    )

    cleaned = plugin.transform(frame)

    assert len(cleaned) == 1
    assert cleaned.iloc[0]["symbol"] == "BTC"
    assert float(cleaned.iloc[0]["price_usd"]) == 99123.5


def test_registry_raises_for_unknown_source_type() -> None:
    with pytest.raises(ValueError):
        get_data_source_plugin("stocks")
