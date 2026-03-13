from datetime import datetime, timezone

import pandas as pd

from app.services.data_transformation_service import prepare_analytic_records, transform_data


def test_transform_data_cleans_nulls_and_converts_types() -> None:
    df = pd.DataFrame(
        [
            {"value": "10", "event_time": "2026-03-13T10:00:00Z", "label": "A"},
            {"value": "", "event_time": "2026-03-13T11:00:00Z", "label": "B"},
            {"value": "20", "event_time": "2026-03-13T12:00:00Z", "label": "C"},
        ]
    )

    cleaned = transform_data(df)

    assert len(cleaned) == 2
    assert pd.api.types.is_numeric_dtype(cleaned["value"])
    assert str(cleaned["event_time"].dtype).startswith("datetime64")


def test_prepare_analytic_records_serializes_datetime() -> None:
    df = pd.DataFrame(
        {
            "metric": [1],
            "ts": [datetime(2026, 3, 13, 10, 0, tzinfo=timezone.utc)],
        }
    )

    records = prepare_analytic_records(df)

    assert records[0]["metric"] == 1
    assert isinstance(records[0]["ts"], str)
    assert records[0]["ts"].startswith("2026-03-13T10:00:00")
