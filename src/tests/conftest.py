from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy import delete, text
from messenger.database.config import settings
from messenger.main import app
from messenger.api.dependencies import get_session
from messenger.utils.password import get_hash_password
from messenger.database.models import UserORM, RefreshSessionORM, ChatORM, MessageORM
import pytest_asyncio
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.pool import NullPool
from faker import Faker
from fastapi.testclient import TestClient


fake = Faker()


# Create engine and session factory specifically for the test database
test_engine = create_async_engine(
    url=settings.TEST_DATABASE_URL,
    echo=False,
    poolclass=NullPool # disable connection pooling for tests
)

session_factory = async_sessionmaker(
    test_engine,
    expire_on_commit=False
)

# Override get_session dependencies for tests
async def override_get_session():
    async with session_factory() as session:
        yield session

# Overrides dependencies before tests and then reset them after tests are finished
@pytest.fixture(autouse=True)
def clear_app_dependencies():
    app.dependency_overrides[get_session] = override_get_session

    yield

    app.dependency_overrides.clear()

# Use dummy client for testing app without starting the server
@pytest_asyncio.fixture
async def get_client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        follow_redirects=False
    ) as client:
        yield client

# Clean test database after every test
# @pytest_asyncio.fixture(autouse=True)
# async def clean_database():

#     yield

#     async with session_factory() as session:
#         await session.execute(delete(RefreshSessionORM))
#         await session.execute(delete(MessageORM))
#         await session.execute(delete(ChatORM))
#         await session.execute(delete(UserORM))
#         await session.commit()

@pytest_asyncio.fixture(autouse=True)
async def clean_database():

    yield

    async with session_factory() as session:
        await session.execute(
            text("""TRUNCATE TABLE refresh_sessions, messages, chats, users RESTART IDENTITY CASCADE""")
        )
        await session.commit()

# Create fake user and save in DB for Login test logic
@pytest_asyncio.fixture
async def create_test_user():
    password = "12345678Aa"

    async with session_factory() as session:
        user = UserORM(
            username="alex",
            email="alex@example.com",
            hash_password=get_hash_password(password)
        )

        session.add(user)
        await session.commit()

    return {
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "password": password
    }


# Create multiple users with unique values (except for password)
@pytest_asyncio.fixture
async def create_test_users():
    async def _create_users(n: int):
        password = "12345678Aa"
        users = []

        async with session_factory() as session:
            for _ in range(n):
                username = fake.unique.user_name()
                email = fake.unique.email()

                user = UserORM(
                    email=email,
                    username=username,
                    hash_password=get_hash_password(password)
                )


                session.add(user)
                users.append(user)

            await session.commit()

        users = [{
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "password": password
        } for user in users]

        return users
    return _create_users 


@pytest_asyncio.fixture
async def create_test_chat():
    async def _create_chat(user_1_id: int, user_2_id: int):
        async with session_factory() as session:
            chat = ChatORM(
                user_1_id=user_1_id,
                user_2_id=user_2_id
            )

            session.add(chat)
            await session.commit()

        return {
            "chat_id": chat.id,
            "user_1_id": user_1_id,
            "user_2_id": user_2_id
        }

    return _create_chat

@pytest_asyncio.fixture
async def create_test_messages():
    async def _create_messages(n: int, sender_id: int, chat_id: int):
        messages = []

        async with session_factory() as session:
            for _ in range(n):
                message_text = fake.text(max_nb_chars=100)

                message = MessageORM(
                    chat_id=chat_id,
                    sender_id=sender_id,
                    content=message_text
                )

                messages.append(message)
                session.add(message)

            await session.commit()

        return [{
            "chat_id": message.chat_id,
            "id": message.id,
            "content": message.content,
            "sender_id": message.sender_id
        } for message in messages]

    return _create_messages

@pytest.fixture
def websocket_client():
    with TestClient(app) as client:
        yield client

@pytest.fixture
def websocket_client_2():
    with TestClient(app) as client:
        yield client