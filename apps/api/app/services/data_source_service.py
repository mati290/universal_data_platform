import json
from io import StringIO
from uuid import UUID

import pandas as pd
from sqlalchemy import delete, func, select

from app.core.db import SessionLocal
from app.models.data_source import CsvUploadSummary, DataSource, DataSourceCreate
from app.models.tables import DatasetORM, RawDataORM, SourceORM


class DataSourceService:
    @staticmethod
    def _as_uuid(source_id: str) -> UUID:
        try:
            return UUID(source_id)
        except ValueError as exc:
            raise KeyError(source_id) from exc

    @staticmethod
    def _to_schema(source: SourceORM, rows_count: int) -> DataSource:
        return DataSource(
            id=str(source.id),
            name=source.name,
            source_type=source.source_type,
            description=source.description,
            created_at=source.created_at,
            rows_count=rows_count,
        )

    def create(self, payload: DataSourceCreate) -> DataSource:
        with SessionLocal() as db:
            source = SourceORM(
                name=payload.name,
                source_type=payload.source_type,
                description=payload.description,
            )
            db.add(source)
            db.flush()

            dataset = DatasetORM(source_id=source.id, name=f"{source.name}-default")
            db.add(dataset)
            db.commit()
            db.refresh(source)

            return self._to_schema(source=source, rows_count=0)

    def list_sources(self) -> list[DataSource]:
        with SessionLocal() as db:
            sources = db.execute(select(SourceORM).order_by(SourceORM.created_at)).scalars().all()
            counts_query = select(RawDataORM.source_id, func.count(RawDataORM.id)).group_by(RawDataORM.source_id)
            counts = {source_id: int(count) for source_id, count in db.execute(counts_query).all()}

            return [self._to_schema(source=source, rows_count=counts.get(source.id, 0)) for source in sources]

    def exists(self, source_id: str) -> bool:
        source_uuid = self._as_uuid(source_id)
        with SessionLocal() as db:
            stmt = select(SourceORM.id).where(SourceORM.id == source_uuid)
            return db.execute(stmt).scalar_one_or_none() is not None

    def upload_csv(self, source_id: str, raw_bytes: bytes) -> CsvUploadSummary:
        source_uuid = self._as_uuid(source_id)

        text = raw_bytes.decode("utf-8")
        frame = pd.read_csv(StringIO(text))
        normalized = frame.where(pd.notna(frame), None)
        rows = json.loads(normalized.to_json(orient="records", date_format="iso"))

        with SessionLocal() as db:
            source = db.get(SourceORM, source_uuid)
            if source is None:
                raise KeyError(source_id)

            db.execute(delete(RawDataORM).where(RawDataORM.source_id == source_uuid))

            if rows:
                db.add_all([RawDataORM(source_id=source_uuid, raw_json=row) for row in rows])

            db.commit()

        return CsvUploadSummary(
            source_id=source_id,
            rows_loaded=len(rows),
            columns=list(frame.columns),
        )

    def fetch_rows(self, source_id: str, limit: int) -> tuple[int, list[dict[str, object]]]:
        source_uuid = self._as_uuid(source_id)

        with SessionLocal() as db:
            source_exists = db.execute(select(SourceORM.id).where(SourceORM.id == source_uuid)).scalar_one_or_none()
            if source_exists is None:
                raise KeyError(source_id)

            total_stmt = select(func.count(RawDataORM.id)).where(RawDataORM.source_id == source_uuid)
            total = int(db.execute(total_stmt).scalar_one() or 0)

            rows_stmt = (
                select(RawDataORM.raw_json)
                .where(RawDataORM.source_id == source_uuid)
                .order_by(RawDataORM.id)
                .limit(limit)
            )
            rows = list(db.execute(rows_stmt).scalars().all())

            return total, rows

    def ingest_raw_records(self, source_id: str, records: list[dict[str, object]]) -> int:
        source_uuid = self._as_uuid(source_id)

        with SessionLocal() as db:
            source_exists = db.execute(select(SourceORM.id).where(SourceORM.id == source_uuid)).scalar_one_or_none()
            if source_exists is None:
                raise KeyError(source_id)

            if records:
                db.add_all([RawDataORM(source_id=source_uuid, raw_json=record) for record in records])
                db.commit()
            return len(records)

    def delete(self, source_id: str) -> None:
        source_uuid = self._as_uuid(source_id)

        with SessionLocal() as db:
            source = db.get(SourceORM, source_uuid)
            if source is None:
                raise KeyError(source_id)

            db.delete(source)
            db.commit()


data_source_service = DataSourceService()
