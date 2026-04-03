import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Union
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.users import User
from app.config import settings
import logging
import time

logger = logging.getLogger(__name__)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash using direct bcrypt.
    """
    try:
        # bcrypt requires bytes
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    """
    Hash a password using direct bcrypt.
    Note: Bcrypt has a 72-byte limit. We truncate to ensure stability if needed,
    though usually passwords this long are rare in this context.
    """
    password_bytes = password.encode('utf-8')
    # If the password is extremely long, we hash it first to fit in 72 bytes
    # or just truncate. passlib used to handle this, but for simplicity here we truncate.
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
        
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def authenticate_user(db: AsyncSession, email: str, password: str) -> Union[User, bool]:
    start_time = time.time()
    try:
        result = await db.execute(select(User).filter(User.email == email))
        user = result.scalars().first()
        if not user:
            return False
        if not verify_password(password, user.hashed_password):
            return False
        
        elapsed = time.time() - start_time
        if elapsed > 1:
            logger.warning(f"Slow authentication for {email}: {elapsed:.2f}s")
        
        return user
    except Exception as e:
        logger.error(f"Authentication error for {email}: {str(e)}")
        return False
