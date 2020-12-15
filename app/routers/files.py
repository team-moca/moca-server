from app.dependencies import get_current_verified_user
import os
from fastapi import APIRouter, HTTPException, status, Depends
from setuptools_scm import get_version
from starlette.responses import FileResponse
from app.schemas import Info, UserResponse

router = APIRouter(prefix="/files", tags=["files"])


@router.get("/{filename}")
async def get_file(filename: str, current_user: UserResponse = Depends(get_current_verified_user)):
    """Get a file by its filename. Files can be images, videos or documents."""

    path = f"storage/{filename}"

    # Check if user is allowed to read this file
    # TODO

    # Get file from storage/
    if os.path.isfile(path):
        # Return file with correct file type
        return FileResponse(path)

    raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File {filename} does not exist.",
        )