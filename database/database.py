from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from utils.config import Config
from database.models import Base


engine = create_async_engine(
    Config.DATABASE_URL,
    echo=True
)

async_session = async_sessionmaker(engine, expire_on_commit=False)


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)