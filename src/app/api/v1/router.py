from fastapi import APIRouter
from src.app.api.v1.routers.auth import router as auth_router
from src.app.api.v1.routers.search_profile import router as search_profile_router
from src.app.api.v1.routers.schedule import router as schedule_router
from src.app.api.v1.routers.search_run import router as search_run_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(search_profile_router)
api_router.include_router(schedule_router)
api_router.include_router(search_run_router)
