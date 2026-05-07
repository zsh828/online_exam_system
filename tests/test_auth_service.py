import pytest
from src.database import InMemoryDatabase
from src.services import UserService
from src.models import User


@pytest.fixture
def db():
    return InMemoryDatabase()

@pytest.fixture
def user_service(db):
    return UserService(db)

class TestRegister:
    def test_register_student_success(self, user_service, db):
        success, msg, user = user_service.register("alice", "Pass1234", "student")
        assert success is True
        assert msg == "Registration successful"
        assert user is not None
        assert user.username == "alice"
        assert user.role == "student"
        assert user.password_hash != "Pass1234"  # Should be hashed
        assert len(user.password_hash) > 0

    def test_register_teacher_success(self, user_service, db):
        success, msg, user = user_service.register("bob", "Teacher1", "teacher")
        assert success is True
        assert user.role == "teacher"

    def test_register_weak_password_no_letters(self, user_service):
        success, msg, user = user_service.register("charlie", "12345678", "student")
        assert success is False
        assert "Password must be at least 8 characters" in msg

    def test_register_weak_password_no_numbers(self, user_service):
        success, msg, user = user_service.register("dave", "abcdefgh", "student")
        assert success is False
        assert "Password must be at least 8 characters" in msg

    def test_register_short_password(self, user_service):
        success, msg, user = user_service.register("eve", "Abc1", "student")
        assert success is False
        assert "Password must be at least 8 characters" in msg

    def test_register_duplicate_username(self, user_service, db):
        user_service.register("frank", "Frank1234", "student")
        success, msg, user = user_service.register("frank", "Frank5678", "student")
        assert success is False
        assert "Username already exists" in msg

    def test_register_invalid_role(self, user_service):
        success, msg, user = user_service.register("grace", "Grace1234", "admin")
        assert success is False
        assert "Invalid role" in msg

class TestLogin:
    def test_login_success(self, user_service, db):
        user_service.register("harry", "Harry1234", "student")
        success, msg, user = user_service.login("harry", "Harry1234")
        assert success is True
        assert msg == "Login successful"
        assert user is not None
        assert user.username == "harry"

    def test_login_wrong_password(self, user_service, db):
        user_service.register("ivan", "Ivan1234", "student")
        success, msg, user = user_service.login("ivan", "WrongPass1")
        assert success is False
        assert "Incorrect password" in msg

    def test_login_nonexistent_user(self, user_service):
        success, msg, user = user_service.login("nonexistent", "AnyPass1")
        assert success is False
        assert "User not found" in msg