import pytest
from src.database import InMemoryDatabase
from src.services import QuestionService
from src.models import Question


@pytest.fixture
def db():
    return InMemoryDatabase()

@pytest.fixture
def question_service(db):
    return QuestionService(db)

@pytest.fixture
def valid_question_data():
    return {
        "q_type": "single",
        "content": "What is 2+2?",
        "options": ["3", "4", "5", "6"],
        "correct_answer": "4",
        "category": "math"
    }

class TestCreateQuestion:
    def test_create_single_choice(self, question_service, db, valid_question_data):
        success, msg, question = question_service.create_question(1, valid_question_data)
        assert success is True
        assert msg == "Question created successfully"
        assert question is not None
        assert question.question_id == 1
        assert question.category == "math"

    def test_create_multiple_choice(self, question_service, db):
        data = {
            "q_type": "multiple",
            "content": "Select fruits",
            "options": ["Apple", "Banana", "Carrot"],
            "correct_answer": ["Apple", "Banana"],
            "category": "biology"
        }
        success, msg, question = question_service.create_question(1, data)
        assert success is True
        assert question.q_type == "multiple"

    def test_create_true_false(self, question_service, db):
        data = {
            "q_type": "true_false",
            "content": "The sky is blue.",
            "options": ["True", "False"],
            "correct_answer": True,
            "category": "science"
        }
        success, msg, question = question_service.create_question(1, data)
        assert success is True
        assert question.correct_answer is True

    def test_create_invalid_type(self, question_service, db, valid_question_data):
        valid_question_data["q_type"] = "essay"
        success, msg, question = question_service.create_question(1, valid_question_data)
        assert success is False
        assert "Invalid question data" in msg

    def test_create_missing_field(self, question_service, db, valid_question_data):
        del valid_question_data["content"]
        success, msg, question = question_service.create_question(1, valid_question_data)
        assert success is False
        assert "Invalid question data" in msg

class TestDeleteQuestion:
    def test_delete_existing_question(self, question_service, db, valid_question_data):
        question_service.create_question(1, valid_question_data)
        success, msg = question_service.delete_question(1)
        assert success is True
        assert msg == "Question deleted successfully"
        assert db.get_question(1) is None

    def test_delete_nonexistent_question(self, question_service):
        success, msg = question_service.delete_question(999)
        assert success is False
        assert "Question not found" in msg

class TestUpdateQuestion:
    def test_update_existing_question(self, question_service, db, valid_question_data):
        question_service.create_question(1, valid_question_data)
        new_data = {
            "q_type": "single",
            "content": "Updated content",
            "options": ["A", "B"],
            "correct_answer": "A",
            "category": "math"
        }
        success, msg, question = question_service.update_question(1, new_data)
        assert success is True
        assert question.content == "Updated content"
        # Original creation time should be preserved
        assert question.created_at > 0

    def test_update_nonexistent_question(self, question_service, valid_question_data):
        success, msg, question = question_service.update_question(999, valid_question_data)
        assert success is False
        assert "Question not found" in msg

class TestQueryByCategory:
    def test_query_empty_category(self, question_service):
        success, msg, questions = question_service.query_by_category("nonexistent")
        assert success is True
        assert questions == []

    def test_query_existing_category(self, question_service, db, valid_question_data):
        question_service.create_question(1, valid_question_data)
        success, msg, questions = question_service.query_by_category("math")
        assert success is True
        assert len(questions) == 1
        assert questions[0].category == "math"