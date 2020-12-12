from app.dependencies import get_current_user, get_current_verified_user
from fastapi.param_functions import Depends
from app.schemas import RegisterRequest, User, VerifyRequest
from fastapi import APIRouter

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.get("/me", response_model=User)
async def get_me(current_user: User = Depends(get_current_verified_user)):
    return current_user


@router.get("/{username}")
async def get_user(username: str):
    return {"username": username}

@router.post("/")
async def register_user(register_request: RegisterRequest):
    return {}

@router.post("/verify")
async def verify_user(verify_request: VerifyRequest):
    return {}