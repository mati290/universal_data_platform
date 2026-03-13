from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.models.data_source import CsvUploadSummary
from app.services import data_source_service

router = APIRouter(tags=["upload"])


@router.post("/upload", response_model=CsvUploadSummary)
async def upload_csv(file: UploadFile = File(...), source_id: str = Form(...)) -> CsvUploadSummary:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are supported.",
        )

    try:
        content = await file.read()
        return data_source_service.upload_csv(source_id=source_id, raw_bytes=content)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found.") from None
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV file must be UTF-8 encoded.",
        ) from None
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid CSV: {exc}") from exc
