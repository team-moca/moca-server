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


@router.get("/{username}")
async def get_user(username: str):
    return {"username": username}

@router.post("/", response_model=UserResponse)
async def register_user(register_request: RegisterRequest, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=register_request.username)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A user with this username is already registered")
    return crud.create_user(db=db, user=register_request)

@router.post("/verify")
async def verify_user(verify_request: VerifyRequest, db: Session = Depends(get_db)):
    return crud.verify_user(db, verify_request)