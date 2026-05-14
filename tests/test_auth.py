import pytest
from src.database import InMemoryDatabase
from src.services import AuthService


@pytest.fixture
def db():
    return InMemoryDatabase()

@pytest.fixture
def auth_service(db):
    return AuthService(db)

def test_register_success_student(auth_service):
    result = auth_service.register("student1", "password123", "student")
    assert result["success"] is True
    assert "user_id" in result

def test_register_success_teacher(auth_service):
    result = auth_service.register("teacher1", "password123", "teacher")
    assert result["success"] is True

def test_register_duplicate_username(auth_service):
    auth_service.register("user1", "password123", "student")
    result = auth_service.register("user1", "password456", "student")
    assert result["success"] is False
    assert "already exists" in result["message"]

def test_register_invalid_role(auth_service):
    result = auth_service.register("user1", "password123", "admin")
    assert result["success"] is False

def test_register_weak_password(auth_service):
    result = auth_service.register("user1", "123", "student")
    assert result["success"] is False
    assert "at least 6 characters" in result["message"]

def test_login_success(auth_service):
    auth_service.register("user1", "password123", "student")
    result = auth_service.login("user1", "password123")
    assert result["success"] is True
    assert result["role"] == "student"

def test_login_wrong_password(auth_service):
    auth_service.register("user1", "password123", "student")
    result = auth_service.login("user1", "wrongpassword")
    assert result["success"] is False

def test_login_non_existent_user(auth_service):
    result = auth_service.login("nouser", "password123")
    assert result["success"] is False