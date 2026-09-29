from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from messenger.schemas.auth import LoginUser, RegisterUser, Username
from messenger.utils.password import get_hash_password, verify_password
from messenger.utils.hash_token import get_hash_token, verify_hash_token
from messenger.api.dependencies import get_session, get_current_refresh_session
from messenger.database.models import UserORM, RefreshSessionORM
from messenger.utils.jwt.jwt import create_access_token
from messenger.utils.jwt.refresh_token import create_refresh_token, decode_refresh_token
from fastapi import Response, Cookie
import jwt
from datetime import datetime, timezone


router = APIRouter()

# ================================= (POST) Register User =================================
@router.post("/register/", status_code=200)
async def register(
    user: RegisterUser,
    session: AsyncSession = Depends(get_session)
):
    existing_user = await session.scalar(select(UserORM).where(UserORM.email == user.email))

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "email_exists",
                "message": "Account with this email already exists"
            }
        )

    existing_username = await session.scalar(select(UserORM).where(UserORM.username == user.username))

    if existing_username:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "username_exists",
                "message": "This username is already taken"
            }
        )

    hash_password = get_hash_password(user.password)

    new_user = UserORM(
        username=user.username,
        email=user.email,
        hash_password=hash_password
    )

    session.add(new_user)
    await session.commit()

    return {"message": "User registered successfully"}

# ================================= (GET) Check Username =================================
@router.get("/check-username/")
async def check_username(
    username: Username,
    session: AsyncSession = Depends(get_session)
):
    existing_username = await session.scalar(select(UserORM).where(UserORM.username == username))

    if existing_username:
        return {
            "available": False,
            "message": "This username is already taken"
        }

    return {
        "available": True,
        "message": "Username is available"
    }

# ================================= (POST) Login User =================================
@router.post("/login/", status_code=200)
async def login(
    user: LoginUser,
    response: Response,
    session: AsyncSession = Depends(get_session)
):
    existing_user = await session.scalar(select(UserORM).where(UserORM.email == user.email))

    if not existing_user:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "invalid_credentials",
                "message": "Invalid email or password"
            }
        )

    if not verify_password(user.password, existing_user.hash_password):
        raise HTTPException(
            status_code=401,
            detail={
                "error": "invalid_credentials",
                "message": "Invalid email or password"
            }
        )

    access_token = create_access_token(existing_user.id)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=900
    )

    # Create refresh token and set up a cookie for it
    expires_at, refresh_token = create_refresh_token(existing_user.id)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=172800
    )

    # Save refresh session for further validation
    refresh_session = RefreshSessionORM(
        user_id=existing_user.id,
        hash_token=get_hash_token(refresh_token),
        expires_at=expires_at
    )

    session.add(refresh_session)
    await session.commit()

    return {"message": "Login successful"}

# ================================= (POST) Validate refresh token =================================
@router.post("/auth/refresh/", status_code=200)
async def validate_refresh_token(
    response: Response,
    refresh_session: RefreshSessionORM = Depends(get_current_refresh_session)
):
    access_token = create_access_token(refresh_session.user_id)

    response.set_cookie(
        key="access_token",
        value=access_token,
        secure=False,
        httponly=True,
        samesite="lax",
        max_age=900
    )

    return {"message": "Token created successfully"}
    