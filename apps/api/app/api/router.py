from fastapi import APIRouter

from app.api.routes.data_sources import router as data_sources_router
from app.api.routes.health import router as health_router
from app.api.routes.raw_data import router as raw_data_router
from app.api.routes.sources import router as sources_router
from app.api.routes.upload import router as upload_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(sources_router)
api_router.include_router(data_sources_router)
api_router.include_router(raw_data_router)
api_router.include_router(upload_router)
