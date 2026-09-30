from fastapi import APIRouter, Request, WebSocket
from fastapi.templating import Jinja2Templates
from messenger.api.dependencies import get_current_user, get_session
from messenger.database.models import UserORM, ChatORM, MessageORM
from fastapi import Depends
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, case, and_
from sqlalchemy.orm import aliased
from messenger.schemas.auth import Username
from fastapi.exceptions import HTTPException

from messenger.utils.jwt.jwt import decode_access_token


router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[3]

templates = Jinja2Templates(
    directory=BASE_DIR / "frontend" / "templates"
)

@router.get("/chats/")
async def chats(
    request: Request
):
    return templates.TemplateResponse(
        request=request,
        name="chats.html"
    )

# Get chats for current user
@router.get("/api/chats/", status_code=200)
async def get_user_chats(
    current_user: UserORM = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):

    user_1 = aliased(UserORM)
    user_2 = aliased(UserORM)

    query = or_(
        ChatORM.user_1_id == current_user.id,
        ChatORM.user_2_id == current_user.id
    )

    stmt = select(ChatORM.id, case((ChatORM.user_1_id == current_user.id,
                                   user_2.username), else_=user_1.username).label("username")) \
        .join(user_1, ChatORM.user_1_id == user_1.id) \
        .join(user_2, ChatORM.user_2_id == user_2.id) \
        .where(query)

    result = await session.execute(stmt)
    rows = result.all()

    return [
        {
            "chat_id": row.id,
            "username": row.username
        } for row in rows
    ]

# Search for username to initiate a new chat
@router.get("/api/users/search/", status_code=200)
async def search_user(
    username: Username,
    current_user: UserORM = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    existing_user = await session.scalar(select(UserORM).where(UserORM.username == username))

    if existing_user is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "not_found",
                "message": "User not found"
            }
        )

    if existing_user.id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "self_search",
                "message": "You can't search for yourself"
            }
        )

    return {
        "user_id": existing_user.id,
        "username": existing_user.username
    }

# Create a new chat or get the existing chat
@router.post("/api/chats/")
async def create_new_chat(
    target_user_id: int,
    current_user: UserORM = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    if target_user_id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "self_chat",
                "message": "You cannot create a new chat with yourself"
            }
        )

    target_user_exists = await session.scalar(select(UserORM).where(UserORM.id == target_user_id))

    if target_user_exists is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "not_found",
                "message": "User not found"
            }
        )
    
    query = or_(
        and_(ChatORM.user_2_id == current_user.id, ChatORM.user_1_id == target_user_id),
        and_(ChatORM.user_2_id == target_user_id, ChatORM.user_1_id == current_user.id)
    )

    stmt = select(ChatORM).where(query)
    result = await session.execute(stmt)
    existing_chat = result.scalar_one_or_none()

    if existing_chat is None:
        new_chat = ChatORM(
            user_1_id=current_user.id,
            user_2_id=target_user_id
        )

        session.add(new_chat)
        await session.commit()

        return {"chat_id": new_chat.id}

    return {"chat_id": existing_chat.id}

# Get messages history for current chat
@router.get("/api/chats/{chat_id}/messages")
async def get_chat_messages(
    chat_id: int,
    current_user: UserORM = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    stmt = select(ChatORM).where(and_(
        ChatORM.id == chat_id,
        or_(
            ChatORM.user_1_id == current_user.id,
            ChatORM.user_2_id == current_user.id
        )
    ))

    result = await session.execute(stmt)
    chat = result.scalar_one_or_none()

    if chat is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "not_found",
                "message": "Chat not found"
            }
        )

    messages_stmt = select(MessageORM) \
        .order_by(MessageORM.created_at) \
        .where(MessageORM.chat_id == chat.id)
    messages = await session.scalars(messages_stmt)
    messages = messages.all()

    return [
        {
            "message_id": message.id,
            "sender_id": message.sender_id,
            "content": message.content,
            "created_at": message.created_at
        } for message in messages
    ]


@router.websocket("/chats/ws/")
async def websocket_handler(
    websocket: WebSocket,
    session: AsyncSession = Depends(get_session)
):
    connections: dict[int, set[WebSocket]] = dict()
    await websocket.accept()


    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message was: {data}")
        token = websocket.cookies.get("access_token")

        user_id = decode_access_token(token)
        await websocket.send_text(f"Your user id is: {user_id}")

        connections.setdefault(user_id, set()).add(websocket)

        user = await session.scalar(select(UserORM).where(UserORM.id == user_id))

        

