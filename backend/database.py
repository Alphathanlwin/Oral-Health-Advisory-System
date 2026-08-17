from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config import settings

connect_args = {}
if settings.DATABASE_URL.startswith("postgresql"):
    connect_args = {
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
    }

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    connect_args=connect_args,
)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
