import pytest
from unittest.mock import AsyncMock, MagicMock
from .helpers import mock_session

@pytest.fixture
def app_with_mock_db():
    from src.main import app
    from src.infrastructure.database.connection import get_db
    db = mock_session()

    async def override_get_db():
        yield db
    app.dependency_overrides[get_db] = override_get_db
    yield (app, db)
    app.dependency_overrides.clear()

@pytest.fixture
def any_async_mock():
    return AsyncMock()
