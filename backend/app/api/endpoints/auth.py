from fastapi import APIRouter, Depends, HTTPException, status, Response
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta
from app.config import settings
from app.core.database import get_db
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt
from app.core.security import (
    authenticate_user, 
    create_access_token, 
    get_password_hash,
    verify_password
)
from app.models.users import User, UserRole
from pydantic import BaseModel, EmailStr

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_current_user(db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    result = await db.execute(select(User).filter(User.email == email))
    user = result.scalars().first()
    if user is None:
        raise credentials_exception
    return user

router = APIRouter()

class UserCreate(BaseModel):
    email: EmailStr
    phone: str
    password: str
    first_name: str
    last_name: str
    role: UserRole = UserRole.TENANT
    terms_accepted: bool

class UserOut(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str] = None
    role: UserRole

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# Simple in-memory rate limiter for demo
from collections import defaultdict
import time

login_attempts = defaultdict(list)
register_attempts = defaultdict(list)

def check_rate_limit(key, attempts_list, limit, window=3600):
    now = time.time()
    # Remove attempts older than window
    attempts_list[:] = [t for t in attempts_list if now - t < window]
    if len(attempts_list) >= limit:
        return False
    attempts_list.append(now)
    return True

def is_kenyan_ip(ip: str):
    # Simulated geo-fencing: Real apps use GeoIP databases
    # For demo, allow all but can be toggled
    return True 

@router.post("/register", response_model=Token)
async def register(response: Response, user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    if not is_kenyan_ip("dynamic"): # IP would come from request headers
         raise HTTPException(status_code=403, detail="Registration is only allowed from Kenya.")

    if (not check_rate_limit(user_in.email, register_attempts[user_in.email], 50)):
        raise HTTPException(status_code=429, detail="Too many registration attempts. Please try again later.")

    if not user_in.terms_accepted:
        raise HTTPException(status_code=400, detail="You must accept the terms of service")
    
    result = await db.execute(select(User).filter(User.email == user_in.email))
    user = result.scalars().first()
    if user:
        raise HTTPException(status_code=400, detail="A user with this email already exists.")
    
    new_user = User(
        email=user_in.email,
        phone=user_in.phone,
        hashed_password=get_password_hash(user_in.password),
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        role=user_in.role
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.email}, expires_delta=access_token_expires
    )
    
    # Set HttpOnly Cookie
    response.set_cookie(
        key="access_token", value=f"Bearer {access_token}", 
        httponly=True, max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax", secure=False # Set secure=True in production
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    if not check_rate_limit(form_data.username, login_attempts[form_data.username], 3):
        raise HTTPException(status_code=429, detail="Too many login attempts. Account temporarily locked.")

    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    # Set HttpOnly Cookie
    response.set_cookie(
        key="access_token", value=f"Bearer {access_token}", 
        httponly=True, max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax", secure=False # Set secure=True in production
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/reset-password")
async def reset_password(email: EmailStr, db: AsyncSession = Depends(get_db)):
    # Placeholder for password reset logic (sending email)
    result = await db.execute(select(User).filter(User.email == email))
    user = result.scalars().first()
    if not user:
        # Don't reveal if user exists for security
        return {"message": "If an account exists for this email, a reset link will be sent."}
    
    # In a real app, generate a token, save it, and send an email
    return {"message": "If an account exists for this email, a reset link will be sent."}
