from fastapi import APIRouter, HTTPException, status

from app.models.data_source import DataSourceCreate
from app.models.source import SourceCreate, SourceRead
from app.services import data_source_service

router = APIRouter(prefix="/sources", tags=["sources"])


@router.post("", response_model=SourceRead, status_code=status.HTTP_201_CREATED)
def create_source(payload: SourceCreate) -> SourceRead:
    created = data_source_service.create(
        DataSourceCreate(
            name=payload.name,
            source_type=payload.type,
            description=payload.description,
        )
    )
    return SourceRead(
        id=created.id,
        name=created.name,
        type=created.source_type,
        description=created.description,
        created_at=created.created_at,
    )


@router.get("", response_model=list[SourceRead])
def list_sources() -> list[SourceRead]:
    records = data_source_service.list_sources()
    return [
        SourceRead(
            id=record.id,
            name=record.name,
            type=record.source_type,
            description=record.description,
            created_at=record.created_at,
        )
        for record in records
    ]


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_source(source_id: str) -> None:
    try:
        data_source_service.delete(source_id)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found.") from None
