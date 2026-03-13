from fastapi import APIRouter, File, HTTPException, Query, UploadFile, status

from app.models.data_source import CsvUploadSummary, DataRowsResponse, DataSource, DataSourceCreate
from app.services import data_source_service

router = APIRouter(prefix="/data-sources", tags=["data-sources"])


@router.post("", response_model=DataSource, status_code=status.HTTP_201_CREATED)
def create_data_source(payload: DataSourceCreate) -> DataSource:
    return data_source_service.create(payload)


@router.get("", response_model=list[DataSource])
def list_data_sources() -> list[DataSource]:
    return data_source_service.list_sources()


@router.post("/{source_id}/upload-csv", response_model=CsvUploadSummary)
async def upload_csv(source_id: str, file: UploadFile = File(...)) -> CsvUploadSummary:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are supported.",
        )

    try:
        content = await file.read()
        return data_source_service.upload_csv(source_id=source_id, raw_bytes=content)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data source not found.") from None
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV file must be UTF-8 encoded.",
        ) from None
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid CSV: {exc}") from exc


@router.get("/{source_id}/data", response_model=DataRowsResponse)
def get_data(source_id: str, limit: int = Query(default=100, ge=1, le=10_000)) -> DataRowsResponse:
    try:
        total_rows, rows = data_source_service.fetch_rows(source_id=source_id, limit=limit)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data source not found.") from None

    return DataRowsResponse(source_id=source_id, total_rows=total_rows, rows=rows)
