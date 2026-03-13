from datetime import datetime

import pandas as pd
from airflow.decorators import dag, task

from udp_shared import utc_now_iso


@dag(
    dag_id="example_pipeline",
    schedule="@daily",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["example", "pandas"],
)
def example_pipeline():
    @task
    def extract() -> list[dict[str, int | str]]:
        return [
            {"country": "PL", "value": 10},
            {"country": "DE", "value": 20},
            {"country": "PL", "value": 15},
        ]

    @task
    def transform(rows: list[dict[str, int | str]]) -> list[dict[str, int | str]]:
        frame = pd.DataFrame(rows)
        summary = frame.groupby("country", as_index=False)["value"].sum()
        summary["processed_at"] = utc_now_iso()
        return summary.to_dict(orient="records")

    @task
    def load(rows: list[dict[str, int | str]]) -> None:
        print(rows)

    load(transform(extract()))


example_pipeline()
