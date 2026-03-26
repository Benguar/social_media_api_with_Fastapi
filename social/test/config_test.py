from social.db.connection import get_db
from unittest.mock import AsyncMock,MagicMock
from social.main import app
import pytest
from fastapi.testclient import TestClient
from social.src.oauth import oauth2_scheme

from social.db.models import User

mock_session = AsyncMock()
mock_user_service = AsyncMock()
def get_mock_session():
    yield mock_session

app.dependency_overrides[get_db] = get_mock_session

@pytest.fixture
def fake_session():
    mock_result = MagicMock()
    
    mock_result.scalar_one.return_value = User(id=1, username="Benguar")
    mock_session.execute.return_value = mock_result
    return mock_session

@pytest.fixture
def fake_user_service():
    return mock_user_service

@pytest.fixture
def test_client():
    return TestClient(app)