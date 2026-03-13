import pandas as pd

from app.services.data_transformation_service import prepare_analytic_records, transform_data


def test_transform_data_removes_nulls_and_converts_types() -> None:
    frame = pd.DataFrame(
        [
            {"city": "Warsaw", "temperature": "19.2", "observed_at": "2026-03-13T10:00:00Z"},
            {"city": "", "temperature": "17.0", "observed_at": "2026-03-13T11:00:00Z"},
            {"city": "Gdansk", "temperature": "17.0", "observed_at": "2026-03-13T11:00:00Z"},
            {"city": "Gdansk", "temperature": "17.0", "observed_at": "2026-03-13T11:00:00Z"},
        ]
    )

    cleaned = transform_data(frame)

    assert len(cleaned) == 2
    assert str(cleaned["temperature"].dtype).startswith(("float", "int"))
    assert str(cleaned["observed_at"].dtype).startswith("datetime64")


def test_prepare_analytic_records_returns_serializable_rows() -> None:
    frame = pd.DataFrame(
        [
            {"city": "Warsaw", "temperature": 19.2},
            {"city": "Gdansk", "temperature": 17.0},
        ]
    )

    records = prepare_analytic_records(frame)

    assert records == [
        {"city": "Warsaw", "temperature": 19.2},
        {"city": "Gdansk", "temperature": 17.0},
    ]
