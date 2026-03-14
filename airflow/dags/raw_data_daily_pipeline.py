from __future__ import annotations

import os
from datetime import datetime
from typing import Any

import pandas as pd
import psycopg
from airflow.decorators import dag, task
from psycopg.types.json import Jsonb

UDP_DB_URL = os.getenv("UDP_DB_URL", "postgresql://udp:udp@postgres:5432/udp")
RAW_DATA_BATCH_LIMIT = int(os.getenv("RAW_DATA_BATCH_LIMIT", "5000"))


def _clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df.copy()

    cleaned = df.copy()
    cleaned = cleaned.replace(r"^\s*$", pd.NA, regex=True)

    # Keep heterogeneous records as long as they contain at least one non-source field.
    non_source_columns = [column for column in cleaned.columns if column != "source_id"]
    if non_source_columns:
        cleaned = cleaned.dropna(how="all", subset=non_source_columns)

    for column in cleaned.columns:
        if column == "source_id":
            continue

        series = cleaned[column]
        if series.dtype == "object":
            numeric_candidate = pd.to_numeric(series, errors="coerce")
            if numeric_candidate.notna().all():
                cleaned[column] = numeric_candidate
                continue

            datetime_candidate = pd.to_datetime(series, errors="coerce", utc=True, format="ISO8601")
            if datetime_candidate.notna().all():
                cleaned[column] = datetime_candidate

    cleaned = cleaned.drop_duplicates().reset_index(drop=True)
    return cleaned


def _to_analytic_records(df: pd.DataFrame) -> list[dict[str, Any]]:
    if df.empty:
        return []

    # Force object dtype first so missing values can be represented as JSON null instead of NaN.
    normalized = df.astype(object).where(pd.notna(df), None)
    datetime_columns = normalized.select_dtypes(include=["datetime64[ns]", "datetime64[ns, UTC]"]).columns
    for column in datetime_columns:
        normalized[column] = normalized[column].map(lambda value: value.isoformat() if value is not None else None)

    return normalized.to_dict(orient="records")


@dag(
    dag_id="raw_data_daily_pipeline",
    schedule="@daily",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["etl", "raw-data", "analytics"],
)
def raw_data_daily_pipeline() -> None:
    @task
    def extract() -> list[dict[str, Any]]:
        query = """
            SELECT source_id::text AS source_id, raw_json
            FROM raw_data
            ORDER BY created_at DESC
            LIMIT %s
        """

        with psycopg.connect(UDP_DB_URL) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (RAW_DATA_BATCH_LIMIT,))
                rows = cursor.fetchall()

        extracted: list[dict[str, Any]] = []
        for source_id, raw_json in rows:
            if isinstance(raw_json, dict):
                extracted.append({"source_id": source_id, **raw_json})

        return extracted

    @task
    def transform(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        frame = pd.DataFrame(rows)
        cleaned = _clean_dataframe(frame)
        return _to_analytic_records(cleaned)

    @task
    def load(rows: list[dict[str, Any]]) -> int:
        create_table_query = """
            CREATE TABLE IF NOT EXISTS analytics_data (
                id BIGSERIAL PRIMARY KEY,
                source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
                record_json JSONB NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
        """

        insert_query = """
            INSERT INTO analytics_data (source_id, record_json)
            VALUES (%s::uuid, %s)
        """

        payload: list[tuple[str, Jsonb]] = []
        for record in rows:
            row_copy = dict(record)
            source_id = row_copy.pop("source_id", None)
            if source_id is None:
                continue
            payload.append((str(source_id), Jsonb(row_copy)))

        with psycopg.connect(UDP_DB_URL) as connection:
            with connection.cursor() as cursor:
                cursor.execute(create_table_query)
                if payload:
                    cursor.executemany(insert_query, payload)
            connection.commit()

        return len(payload)

    load(transform(extract()))


raw_data_daily_pipeline()
