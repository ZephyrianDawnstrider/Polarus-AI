from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.auth.jwt import verify_access_token


oauth2_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/token",
)


async def get_current_username(token: str = Depends(oauth2_scheme)) -> str:
    """Resolve the authenticated username from a Bearer JWT."""

    payload = verify_access_token(token)
    username = payload.get("sub")

    if not isinstance(username, str) or not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return username
