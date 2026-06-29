from typing import Any
from urllib.parse import parse_qs

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field

from app.auth.jwt import create_access_token, verify_access_token


router: APIRouter = APIRouter(prefix="/auth", tags=["Auth"])
oauth2_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/token",
)


class TokenRequest(BaseModel):
    """Temporary token request payload until database-backed auth exists."""

    username: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    """JWT bearer token response."""

    access_token: str
    token_type: str = "bearer"


class CurrentUserResponse(BaseModel):
    """Authenticated user response."""

    username: str
    authenticated: bool = True


async def get_token_username(request: Request) -> str:
    """Read a username from JSON or OAuth2 form-encoded token requests."""

    content_type = request.headers.get("content-type", "")

    if "application/json" in content_type:
        payload = await request.json()
        username = payload.get("username") if isinstance(payload, dict) else None
    else:
        body = (await request.body()).decode("utf-8")
        form_data = parse_qs(body)
        username = form_data.get("username", [None])[0]

    if not isinstance(username, str) or not username.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Username is required",
        )

    return username.strip()


async def get_current_username(token: str = Depends(oauth2_scheme)) -> str:
    """Resolve the authenticated username from an Authorization Bearer token."""

    payload: dict[str, Any] = verify_access_token(token)
    username = payload.get("sub")

    if not isinstance(username, str) or not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return username


@router.post("/token", response_model=TokenResponse)
async def create_token(username: str = Depends(get_token_username)) -> TokenResponse:
    """Create a JWT for the provided username."""

    return TokenResponse(access_token=create_access_token(subject=username))


@router.get("/me", response_model=CurrentUserResponse)
async def read_current_user(
    username: str = Depends(get_current_username),
) -> CurrentUserResponse:
    """Return the currently authenticated user."""

    return CurrentUserResponse(username=username)
