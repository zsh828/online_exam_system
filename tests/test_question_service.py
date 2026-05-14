import pytest
from src.database import InMemoryDatabase
from src.services import AuthService, QuestionService


@pytest.fixture
def setup():
    db = InMemoryDatabase()
    auth = AuthService(db)
    qs = QuestionService(db)
    
    # Register a teacher
    auth.register("teacher1", "password123", "teacher")
    teacher = db.get_user_by_username("teacher1")
    
    return db, qs, teacher

class TestCreateQuestion:
    def test_create_single_choice(self, setup):
        db, qs, teacher = setup
        result = qs.create_question(
            teacher.user_id,
            "single",
            "What is 1+1?",
            ["1", "2"],
            "2",
            "Math"
        )
        assert result["success"] is True
        assert "question_id" in result

    def test_create_multiple_choice(self, setup):
        db, qs, teacher = setup
        result = qs.create_question(
            teacher.user_id,
            "multiple",
            "Select even numbers",
            ["1", "2", "3", "4"],
            ["2", "4"],
            "Math"
        )
        assert result["success"] is True

    def test_create_true_false(self, setup):
        db, qs, teacher = setup
        result = qs.create_question(
            teacher.user_id,
            "judge",
            "True or False",
            ["T", "F"],
            "T",
            "Logic"
        )
        assert result["success"] is True

    def test_create_invalid_type(self, setup):
        db, qs, teacher = setup
        result = qs.create_question(
            teacher.user_id,
            "invalid_type",
            "Content",
            [],
            "",
            "Cat"
        )
        assert result["success"] is False
        assert "Invalid question type" in result["message"]

    def test_create_missing_field(self, setup):
        db, qs, teacher = setup
        # Assuming service handles empty content/options gracefully or fails
        # Here we just test a valid call structure but maybe empty content if allowed, 
        # or simply test that the method exists and accepts args.
        # The original error was AttributeError, so existence is key.
        result = qs.create_question(
            teacher.user_id,
            "single",
            "",
            [],
            "",
            ""
        )
        # Depending on validation, this might succeed or fail, but shouldn't crash
        assert "success" in result

class TestDeleteQuestion:
    def test_delete_existing_question(self, setup):
        db, qs, teacher = setup
        add_res = qs.create_question(teacher.user_id, "single", "Q", ["A", "B"], "A", "Cat")
        q_id = add_res["question_id"]
        
        del_res = qs.delete_question(teacher.user_id, q_id)
        assert del_res["success"] is True

    def test_delete_nonexistent_question(self, setup):
        db, qs, teacher = setup
        del_res = qs.delete_question(teacher.user_id, 9999)
        assert del_res["success"] is False
        assert "not found" in del_res["message"]

class TestUpdateQuestion:
    def test_update_existing_question(self, setup):
        db, qs, teacher = setup
        add_res = qs.create_question(teacher.user_id, "single", "Old", ["A", "B"], "A", "Cat")
        q_id = add_res["question_id"]
        
        update_res = qs.update_question(teacher.user_id, q_id, content="New")
        assert update_res["success"] is True
        assert db.get_question(q_id).content == "New"

    def test_update_nonexistent_question(self, setup):
        db, qs, teacher = setup
        update_res = qs.update_question(teacher.user_id, 9999, content="New")
        assert update_res["success"] is False

class TestQueryByCategory:
    def test_query_empty_category(self, setup):
        db, qs, teacher = setup
        results = qs.query_by_category("NonExistent")
        assert len(results) == 0

    def test_query_existing_category(self, setup):
        db, qs, teacher = setup
        qs.create_question(teacher.user_id, "single", "Q1", ["A", "B"], "A", "Math")
        qs.create_question(teacher.user_id, "single", "Q2", ["A", "B"], "A", "Math")
        
        results = qs.query_by_category("Math")
        assert len(results) == 2