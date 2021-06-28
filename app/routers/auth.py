from fastapi.param_functions import Header
from starlette.responses import Response
from app import crud, models
from datetime import datetime, timedelta
from fastapi.exceptions import HTTPException
from sqlalchemy.orm.session import Session
from app.dependencies import (
    ACCESS_TOKEN_EXPIRE_DAYS,
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
from app.schemas import (
    AuthUser,
    Info,
    RegisterRequest,
    Token,
    UserResponse,
    VerifyRequest,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_agent=Header(None),
    x_moca_client=Header(None),
    db: Session = Depends(get_db),
):
    """Login to the MOCA Server.
    This will return an access token which can be used to authenticate all following requests."""
    user: models.User = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create a new session
    new_session = models.Session(
        user_id=user.user_id,
        name=x_moca_client if x_moca_client else user_agent,
        valid_until=datetime.now() + timedelta(days=30),
    )
    db.add(new_session)
    db.commit()

    access_token_expires = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = create_access_token(
        data={
            "sub": str(user.user_id),
            "username": user.username,
            "jti": str(new_session.session_id),
        },
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh", response_model=Token)
async def refresh(
    user: AuthUser = Depends(get_current_verified_user), db: Session = Depends(get_db)
):
    """Get a refresh token.
    Generating a refresh token will instantly invalidate all previous refresh tokens."""

    current_session = (
        db.query(models.Session)
        .filter(models.Session.session_id == user.session_id)
        .first()
    )
    current_session.valid_until = datetime.now() + timedelta(days=30)

    db.commit()

    access_token_expires = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = create_access_token(
        data={
            "sub": str(user.user_id),
            "username": user.username,
            "jti": user.session_id,
        },
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
async def logout(
    user: AuthUser = Depends(get_current_verified_user), db: Session = Depends(get_db)
):
    """Logout from the current session."""

    db.query(models.Session).filter(
        models.Session.session_id == user.session_id
    ).delete()
    db.commit()


@router.post("/register", response_model=UserResponse)
async def register_user(
    register_request: RegisterRequest, db: Session = Depends(get_db)
):
    """Register a new user.
    The user will have to verify their account via /auth/verify."""
    db_user = crud.get_user_by_username(db, username=register_request.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this username is already registered",
        )
    return crud.create_user(db=db, user=register_request)


@router.post("/verify")
async def verify_user(verify_request: VerifyRequest, db: Session = Depends(get_db)):
    """Verify a user.
    After verification, the user can login via /auth/login."""
    return crud.verify_user(db, verify_request)
