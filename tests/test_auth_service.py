import pytest
from src.database import InMemoryDatabase
from src.services import AuthService


@pytest.fixture
def db():
    return InMemoryDatabase()

@pytest.fixture
def auth_service(db):
    return AuthService(db)

def test_auth_service_register_success(auth_service):
    result = auth_service.register("testuser", "securepass", "student")
    assert result["success"] is True
    assert "user_id" in result

def test_auth_service_login_success(auth_service):
    auth_service.register("testuser", "securepass", "teacher")
    result = auth_service.login("testuser", "securepass")
    assert result["success"] is True
    assert result["role"] == "teacher"

def test_auth_service_invalid_credentials(auth_service):
    result = auth_service.login("nonexistent", "wrongpass")
    assert result["success"] is False