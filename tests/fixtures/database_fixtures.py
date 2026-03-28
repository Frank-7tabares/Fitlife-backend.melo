import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
import os

@pytest.fixture(scope='session')
def db_url():
    return os.getenv('TEST_DATABASE_URL', 'mysql+aiomysql://fitlife_user:fitlife_pass@localhost:3306/fitlife_test_db')

@pytest_asyncio.fixture(scope='function')
async def async_db_session(db_url):
    engine = create_async_engine(db_url, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        async with session.begin():
            yield session
            await session.rollback()
    await engine.dispose()
