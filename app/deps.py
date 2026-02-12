from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .core.database import get_db
from .core.config import settings
from .schemas import TokenData
from .models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[AsyncSession, Depends(get_db)]):
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
        token_data = TokenData(emailId=email)
    except JWTError:
        raise credentials_exception
    
    result = await db.execute(select(User).where(User.emailId == token_data.emailId))
    user = result.scalars().first()
    if user is None:
        raise credentials_exception
    return user
