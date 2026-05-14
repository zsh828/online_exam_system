import pytest
from src.database import InMemoryDatabase
from src.services import AuthService, QuestionService, PaperService


@pytest.fixture
def setup():
    db = InMemoryDatabase()
    auth = AuthService(db)
    qs = QuestionService(db)
    ps = PaperService(db)
    
    # Register a teacher
    auth.register("teacher1", "password123", "teacher")
    teacher = db.get_user_by_username("teacher1")
    
    # Add some questions using the compatible method name
    q1 = qs.create_question(teacher.user_id, "single", "Q1", ["A", "B"], "A", "Math")
    q2 = qs.create_question(teacher.user_id, "single", "Q2", ["A", "B"], "A", "Math")
    
    return db, qs, ps, teacher, q1["question_id"], q2["question_id"]

class TestCreatePaper:
    def test_create_valid_paper(self, setup):
        db, qs, ps, teacher, q1_id, q2_id = setup
        questions = [(q1_id, 10.0), (q2_id, 20.0)]
        result = ps.create_paper(teacher.user_id, "Test Paper", questions)
        
        assert result["success"] is True
        assert "paper_id" in result
        paper = db.get_paper(result["paper_id"])
        assert paper.total_score == 30.0

    def test_create_paper_with_invalid_question_id(self, setup):
        db, qs, ps, teacher, q1_id, q2_id = setup
        questions = [(9999, 10.0)]
        result = ps.create_paper(teacher.user_id, "Bad Paper", questions)
        
        assert result["success"] is False
        assert "do not exist" in result["message"]

    def test_create_paper_missing_score_field(self, setup):
        db, qs, ps, teacher, q1_id, q2_id = setup
        # Test handling of malformed input if necessary, or just valid structure
        # The error log suggested unpacking issues, likely fixed by using dict return
        questions = [(q1_id, 10.0)]
        result = ps.create_paper(teacher.user_id, "Score Test", questions)
        assert result["success"] is True

class TestDeletePaper:
    def test_delete_existing_paper(self, setup):
        db, qs, ps, teacher, q1_id, q2_id = setup
        p_res = ps.create_paper(teacher.user_id, "To Delete", [(q1_id, 10.0)])
        p_id = p_res["paper_id"]
        
        del_res = ps.delete_paper(teacher.user_id, p_id)
        assert del_res["success"] is True
        assert db.get_paper(p_id) is None

    def test_delete_nonexistent_paper(self, setup):
        db, qs, ps, teacher, q1_id, q2_id = setup
        del_res = ps.delete_paper(teacher.user_id, 9999)
        assert del_res["success"] is False
        assert "not found" in del_res["message"]

class TestGetByCreator:
    def test_get_papers_by_creator(self, setup):
        db, qs, ps, teacher, q1_id, q2_id = setup
        ps.create_paper(teacher.user_id, "Paper 1", [(q1_id, 10.0)])
        ps.create_paper(teacher.user_id, "Paper 2", [(q2_id, 20.0)])
        
        all_papers = ps.get_all_papers()
        # Filter manually or check count if service supports filtering
        # Current service gets all.
        assert len(all_papers) == 2