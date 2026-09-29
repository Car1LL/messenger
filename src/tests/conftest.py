from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy import delete
from messenger.database.config import settings
from messenger.main import app
from messenger.api.dependencies import get_session
from messenger.utils.password import get_hash_password
from messenger.database.models import UserORM, RefreshSessionORM
import pytest_asyncio
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.pool import NullPool

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
@pytest_asyncio.fixture(autouse=True)
async def clean_database():

    yield

    async with session_factory() as session:
        await session.execute(delete(RefreshSessionORM))
        await session.execute(delete(UserORM))
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