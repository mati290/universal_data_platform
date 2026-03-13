from __future__ import annotations

from uuid import UUID

import pandas as pd
from sqlalchemy import select

from app.core.db import SessionLocal
from app.models.tables import RawDataORM


def load_raw_data_as_dataframe(source_id: str, limit: int | None = None) -> pd.DataFrame:
    source_uuid = UUID(source_id)

    with SessionLocal() as db:
        stmt = select(RawDataORM.raw_json).where(RawDataORM.source_id == source_uuid).order_by(RawDataORM.id)
        if limit is not None:
            stmt = stmt.limit(limit)

        rows = list(db.execute(stmt).scalars().all())

    if not rows:
        return pd.DataFrame()

    return pd.DataFrame(rows)


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df.copy()

    cleaned = df.copy()
    cleaned = cleaned.replace(r"^\s*$", pd.NA, regex=True)

    # Remove records that still contain null-like values to keep the analytical layer strict.
    cleaned = cleaned.dropna(how="any")

    for column in cleaned.columns:
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


def prepare_analytic_records(df: pd.DataFrame) -> list[dict[str, object]]:
    if df.empty:
        return []

    normalized = df.where(pd.notna(df), None)

    datetime_columns = normalized.select_dtypes(include=["datetime64[ns]", "datetime64[ns, UTC]"]).columns
    for column in datetime_columns:
        normalized[column] = normalized[column].map(lambda value: value.isoformat() if value is not None else None)

    return normalized.to_dict(orient="records")


def run_transformation_pipeline(source_id: str, limit: int | None = None) -> tuple[pd.DataFrame, list[dict[str, object]]]:
    raw_df = load_raw_data_as_dataframe(source_id=source_id, limit=limit)
    cleaned_df = transform_data(raw_df)
    records = prepare_analytic_records(cleaned_df)
    return cleaned_df, records
