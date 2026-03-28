from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from ...config.settings import settings
DATABASE_URL = settings.get_database_url()
_engine_kwargs: dict = {'echo': settings.DEBUG, 'pool_size': 5, 'max_overflow': 10}
_connect = settings.mysql_connect_args()
if _connect:
    _engine_kwargs['connect_args'] = _connect
engine = create_async_engine(DATABASE_URL, **_engine_kwargs)
AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
