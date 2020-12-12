from fastapi import APIRouter
from setuptools_scm import get_version
from app.schemas import Info

router = APIRouter(prefix="/info", tags=["info"])


@router.get("", response_model=Info)
async def get_server_info():
    """Get version information about the server.
    A client should only continue talking to the server if its version is bigger than the last supported version.
    Version numbers follow semantic versioning."""
    return Info(current_version=get_version(), last_supported_version=get_version())
