from app.database import SessionLocal
from datetime import datetime, timedelta
from typing import Optional
from app.schemas import AuthUser
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, status
from passlib.context import CryptContext
from jose import JWTError, jwt

# WARNING! This is a dev key only. DO NOT use this in production.
SECRET_KEY = "f61e42feaed37bec38837b107c4ee1b02c2c0493b240dc5f66865aa1596976f6"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def fake_user(username: str):
    return AuthUser(
        user_id=-1,
        username=username,
        mail="mail@example.com",
        is_verified=True,
        created_at=datetime.now() - timedelta(days=7),
        updated_at=datetime.now(),
        hashed_password="$2b$12$Aipuunq/Af8FqGjLVWLGseSMIBTyg0nZMyS8Nfkt5lvBro.eUp/J2"
    )

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain: str, hashed: str):
    """Verify that a plain text password matches the hashed password."""
    return pwd_context.verify(plain, hashed)

def get_password_hash(password):
    print(f"Hashed password: {pwd_context.hash(password)}")
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str):
    user = fake_user(username + "fakeauthenticate")

    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def fake_decode_token(token):
    return fake_user(token + "fakedecoded")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = fake_decode_token(token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user

async def get_current_verified_user(current_user: AuthUser = Depends(get_current_user)):
    if not current_user.is_verified:
        raise HTTPException(status_code=400, detail="User not verified.")
    return current_user

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()