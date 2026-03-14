from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import psycopg
from airflow.decorators import dag, task
from psycopg.types.json import Jsonb

UDP_DB_URL = os.getenv("UDP_DB_URL", "postgresql://udp:udp@postgres:5432/udp")
CRYPTO_API_URL = os.getenv("CRYPTO_API_URL", "https://api.coingecko.com/api/v3/simple/price")
CRYPTO_IDS = [item.strip() for item in os.getenv("CRYPTO_IDS", "bitcoin,ethereum,aave").split(",") if item.strip()]
CRYPTO_VS_CURRENCY = os.getenv("CRYPTO_VS_CURRENCY", "usd")
CRYPTO_SOURCE_NAME = os.getenv("CRYPTO_SOURCE_NAME", "crypto-coingecko")
CRYPTO_SOURCE_DESCRIPTION = os.getenv(
    "CRYPTO_SOURCE_DESCRIPTION",
    "Scheduled crypto market snapshots fetched from CoinGecko.",
)

SYMBOL_MAP = {
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "aave": "AAVE",
}


def _to_iso_utc(epoch_seconds: int | None) -> str:
    if epoch_seconds is None:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    dt = datetime.fromtimestamp(epoch_seconds, tz=timezone.utc)
    return dt.isoformat().replace("+00:00", "Z")


@dag(
    dag_id="crypto_market_ingest_pipeline",
    schedule="*/30 * * * *",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["crypto", "ingest", "internet"],
)
def crypto_market_ingest_pipeline() -> None:
    @task
    def extract() -> dict[str, dict[str, float | int]]:
        params = {
            "ids": ",".join(CRYPTO_IDS),
            "vs_currencies": CRYPTO_VS_CURRENCY,
            "include_last_updated_at": "true",
        }
        url = f"{CRYPTO_API_URL}?{urlencode(params)}"
        request = Request(url, headers={"User-Agent": "universal-data-platform/1.0"}, method="GET")

        with urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))

        if not isinstance(payload, dict):
            raise ValueError("Unexpected API response format from crypto provider.")

        return payload

    @task
    def transform(payload: dict[str, dict[str, float | int]]) -> list[dict[str, object]]:
        records: list[dict[str, object]] = []

        for asset_id in CRYPTO_IDS:
            market = payload.get(asset_id)
            if not isinstance(market, dict):
                continue

            price_key = CRYPTO_VS_CURRENCY
            if price_key not in market:
                continue

            last_updated = market.get("last_updated_at")
            last_updated_int = int(last_updated) if isinstance(last_updated, (int, float)) else None

            records.append(
                {
                    "symbol": SYMBOL_MAP.get(asset_id, asset_id.upper()),
                    "asset_id": asset_id,
                    "price_usd": float(market[price_key]),
                    "event_time": _to_iso_utc(last_updated_int),
                    "provider": "coingecko",
                }
            )

        if not records:
            raise ValueError("No crypto records extracted from API response.")

        return records

    @task
    def load(records: list[dict[str, object]]) -> int:
        get_source_query = """
            SELECT id::text
            FROM sources
            WHERE name = %s AND source_type = 'crypto'
            ORDER BY created_at
            LIMIT 1
        """
        insert_source_query = """
            INSERT INTO sources (id, name, source_type, description)
            VALUES (%s::uuid, %s, 'crypto', %s)
        """
        insert_dataset_query = """
            INSERT INTO datasets (id, source_id, name)
            VALUES (%s::uuid, %s::uuid, %s)
        """
        insert_raw_data_query = """
            INSERT INTO raw_data (source_id, raw_json)
            VALUES (%s::uuid, %s)
        """

        with psycopg.connect(UDP_DB_URL) as connection:
            with connection.cursor() as cursor:
                cursor.execute(get_source_query, (CRYPTO_SOURCE_NAME,))
                row = cursor.fetchone()

                if row is None:
                    source_id = str(uuid.uuid4())
                    cursor.execute(
                        insert_source_query,
                        (source_id, CRYPTO_SOURCE_NAME, CRYPTO_SOURCE_DESCRIPTION),
                    )
                    cursor.execute(
                        insert_dataset_query,
                        (str(uuid.uuid4()), source_id, f"{CRYPTO_SOURCE_NAME}-default"),
                    )
                else:
                    source_id = str(row[0])

                payload = [(source_id, Jsonb(record)) for record in records]
                cursor.executemany(insert_raw_data_query, payload)

            connection.commit()

        return len(records)

    load(transform(extract()))


crypto_market_ingest_pipeline()