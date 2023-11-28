from groundible_admin.root.settings import Settings
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase

settings = Settings()

engine = create_async_engine(url=str(settings.postgres_url))


async_session = async_sessionmaker(engine, expire_on_commit=False)
