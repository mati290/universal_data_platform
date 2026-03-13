from fastapi import APIRouter, HTTPException, status

from app.models.raw_data import RawDataIngestRequest, RawDataIngestResponse
from app.services import data_source_service

router = APIRouter(prefix="/raw-data", tags=["raw-data"])


@router.post("", response_model=RawDataIngestResponse, status_code=status.HTTP_201_CREATED)
def ingest_raw_data(payload: RawDataIngestRequest) -> RawDataIngestResponse:
    try:
        saved = data_source_service.ingest_raw_records(source_id=payload.source_id, records=payload.records)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found.") from None

    return RawDataIngestResponse(source_id=payload.source_id, records_saved=saved)
