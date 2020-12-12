from fastapi import APIRouter
from setuptools_scm import get_version
from app.schemas import Info

router = APIRouter(
    prefix="/info",
    tags=["info"]
)

@router.get("/", response_model=Info)
async def get_server_info():
    return {
        "current_version": get_version(),
        "last_supported_version": get_version()
    }
