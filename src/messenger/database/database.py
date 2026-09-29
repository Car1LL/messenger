from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from messenger.database.config import settings

engine = create_async_engine(
    url=settings.DATABASE_URL,
    echo=False
)

async_session = async_sessionmaker(engine, expire_on_commit=False)

