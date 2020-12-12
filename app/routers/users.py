from fastapi.exceptions import HTTPException
from starlette.routing import request_response
from app import crud
from sqlalchemy.orm import Session
from app.dependencies import get_current_user, get_current_verified_user, get_db
from fastapi.param_functions import Depends
from app.schemas import RegisterRequest, User, UserResponse, VerifyRequest
from fastapi import APIRouter, status

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: UserResponse = Depends(get_current_verified_user)):
    return current_user
