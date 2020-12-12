from app import crud
from datetime import timedelta
from fastapi.exceptions import HTTPException
from sqlalchemy.orm.session import Session
from app.dependencies import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user,
    create_access_token,
    get_current_verified_user,
    get_db,
    get_hashed_password,
)
from fastapi import APIRouter, status
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordRequestForm
from setuptools_scm import get_version
from app.schemas import Info, RegisterRequest, Token, UserResponse, VerifyRequest

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.user_id), "username": user.username},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh", response_model=Token)
async def refresh(user: UserResponse = Depends(get_current_verified_user)):
    """Get a refresh token."""

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.user_id), "username": user.username},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/", response_model=UserResponse)
async def register_user(
    register_request: RegisterRequest, db: Session = Depends(get_db)
):
    db_user = crud.get_user_by_username(db, username=register_request.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this username is already registered",
        )
    return crud.create_user(db=db, user=register_request)


@router.post("/verify")
async def verify_user(verify_request: VerifyRequest, db: Session = Depends(get_db)):
    return crud.verify_user(db, verify_request)
