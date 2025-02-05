from environs import Env
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from models.vakansiya import Base

env = Env()
env.read_env()

BOT_TOKEN = env.str('BOT_TOKEN')
ADMIN_ID = env.str('ADMIN_ID')
DATABASE_URL = env.str('DATABASE_URL')
CHANNEL_ID = env.str('CHANNEL_ID')

engine = create_async_engine(DATABASE_URL, echo=False)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    async with SessionLocal() as session:
        yield session
