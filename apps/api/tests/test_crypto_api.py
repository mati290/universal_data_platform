from __future__ import annotations

import uuid

from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.db import SessionLocal
from app.main import app

client = TestClient(app)


def test_crypto_live_latest_endpoint_returns_filtered_symbol() -> None:
    symbol = f"TST{uuid.uuid4().hex[:6].upper()}"
    source_id = str(uuid.uuid4())
    dataset_id = str(uuid.uuid4())

    with SessionLocal() as db:
        db.execute(
            text(
                """
                INSERT INTO sources (id, name, source_type, description)
                VALUES (CAST(:id AS UUID), 'crypto-coingecko', 'crypto', 'test live source')
                """
            ),
            {"id": source_id},
        )
        db.execute(
            text(
                """
                INSERT INTO datasets (id, source_id, name)
                VALUES (CAST(:id AS UUID), CAST(:source_id AS UUID), :name)
                """
            ),
            {"id": dataset_id, "source_id": source_id, "name": f"{symbol}-dataset"},
        )
        db.execute(
            text(
                """
                INSERT INTO raw_data (source_id, raw_json)
                VALUES (
                    CAST(:source_id AS UUID),
                    jsonb_build_object(
                        'symbol', CAST(:symbol AS TEXT),
                        'asset_id', 'test-asset',
                        'price_usd', 123.45,
                        'event_time', '2026-03-14T12:00:00Z',
                        'provider', 'test-suite'
                    )
                )
                """
            ),
            {"source_id": source_id, "symbol": symbol},
        )
        db.commit()

    response = client.get(f"/api/v1/crypto/live/latest?symbol={symbol}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_rows"] == 1
    assert payload["rows"][0]["symbol"] == symbol
    assert payload["rows"][0]["price_usd"] == 123.45


def test_crypto_archive_latest_endpoint_returns_filtered_symbol() -> None:
    symbol = f"ARC{uuid.uuid4().hex[:6].upper()}"

    with SessionLocal() as db:
        db.execute(
            text(
                """
                INSERT INTO crypto_csv_history (
                    source_file, s_no, coin_name, symbol, event_time, high, low, open, close, volume, marketcap
                ) VALUES (
                    :source_file, :s_no, :coin_name, :symbol, :event_time,
                    :high, :low, :open, :close, :volume, :marketcap
                )
                """
            ),
            {
                "source_file": "test_archive.csv",
                "s_no": 1,
                "coin_name": "Archive Test Coin",
                "symbol": symbol,
                "event_time": "2026-03-14T13:00:00Z",
                "high": 10.5,
                "low": 9.5,
                "open": 9.8,
                "close": 10.1,
                "volume": 1000.0,
                "marketcap": 500000.0,
            },
        )
        db.commit()

    response = client.get(f"/api/v1/crypto/archive/latest?symbol={symbol}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_rows"] == 1
    assert payload["rows"][0]["symbol"] == symbol
    assert payload["rows"][0]["coin_name"] == "Archive Test Coin"
    assert payload["rows"][0]["close"] == 10.1