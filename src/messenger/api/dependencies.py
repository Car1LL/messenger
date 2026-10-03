from messenger.database.database import async_session
from fastapi import Depends, Cookie, WebSocket
from messenger.utils.jwt.jwt import decode_access_token
from messenger.utils.jwt.refresh_token import decode_refresh_token
from messenger.utils.hash_token import get_hash_token
from messenger.database.models import UserORM, RefreshSessionORM
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi.exceptions import HTTPException, WebSocketException
from starlette import status
import jwt
from datetime import datetime, timezone


# Yields factory session 
async def get_session():
    async with async_session() as session:
        yield session


# Returns current user based on JWT access token
async def get_current_user(
        access_token: str | None = Cookie(default=None),
        session: AsyncSession = Depends(get_session)
) -> UserORM:
    
    if access_token is None:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "not_authenticated",
                "message": "Not authenticated"
            }
        )

    try:
        user_id = decode_access_token(access_token)
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "invalid_token",
                "message": "Invalid or expired token"
            }
        )

    user = await session.scalar(select(UserORM).where(UserORM.id == user_id))

    if not user:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "not_authenticated",
                "message": "User not found"
            }
        )

    return user

async def optional_get_current_user(
        access_token: str | None = Cookie(default=None),
        session: AsyncSession = Depends(get_session)
) -> UserORM | None:

    if access_token is None:
        return None
    
    return await get_current_user(access_token=access_token, session=session)


# Refresh Token
async def get_current_refresh_session(
        session: AsyncSession = Depends(get_session),
        refresh_token: str | None = Cookie(default=None)
) -> RefreshSessionORM: 
    
    if refresh_token is None:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "missing_refresh_token",
                "message": "Refresh Token is missing"
            }
        )

    try:
        decode_refresh_token(refresh_token)
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "invalid_refresh_token",
                "message": "Invalid or expired refresh token"
            }
        )

    hash_token = get_hash_token(refresh_token)

    existing_refresh_session = await session.scalar(select(RefreshSessionORM).where(
        RefreshSessionORM.hash_token == hash_token
    ))

    if existing_refresh_session is None:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "refresh_session_not_found",
                "message": "Refresh session not found"
            }
        )

    if existing_refresh_session.revoked_at is not None:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "refresh_session_revoked",
                "message": "Refresh session has been revoked"
            }
        )

    if existing_refresh_session.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=401,
            detail={
                "error": "refresh_session_expired",
                "message": "Refresh session has expired"
            }
        )

    return existing_refresh_session

# Get current user for websocket endpoint
async def get_current_websocket_user(
        websocket: WebSocket,
        session: AsyncSession = Depends(get_session)
) -> UserORM:
    access_token = websocket.cookies.get("access_token")

    if access_token is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    
    try:    
        user_id = decode_access_token(access_token)
    except jwt.InvalidTokenError:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    user = await session.scalar(select(UserORM).where(UserORM.id == user_id))

    if not user:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    return user
