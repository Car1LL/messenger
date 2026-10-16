from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy import ForeignKey, String, func, DateTime
from datetime import date, datetime, timedelta, timezone, time


DEFAULT_AVATAR_PATH = "/static/assets/avatars/default-user.webp"


class Base(DeclarativeBase):
    pass

class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(nullable=False, unique=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    hash_password: Mapped[str] = mapped_column(nullable=False)
    avatar_path: Mapped[str] = mapped_column(nullable=False, default=DEFAULT_AVATAR_PATH)

class RefreshSessionORM(Base):
    __tablename__ = "refresh_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, unique=False)
    hash_token: Mapped[str] = mapped_column(String(256), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)

class ChatORM(Base):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_1_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user_2_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class MessageORM(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"))
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    content: Mapped[str] = mapped_column(String(512))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())