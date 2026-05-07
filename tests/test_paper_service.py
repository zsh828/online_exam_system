import pytest
from src.database import InMemoryDatabase
from src.services import PaperService, QuestionService
from src.models import Question


@pytest.fixture
def db():
    return InMemoryDatabase()

@pytest.fixture
def question_service(db):
    return QuestionService(db)

@pytest.fixture
def paper_service(db):
    return PaperService(db)

@pytest.fixture
def setup_questions(question_service):
    q1 = {"q_type": "single", "content": "Q1", "options": ["A"], "correct_answer": "A", "category": "cat1"}
    q2 = {"q_type": "single", "content": "Q2", "options": ["B"], "correct_answer": "B", "category": "cat1"}
    _, _, q1_obj = question_service.create_question(1, q1)
    _, _, q2_obj = question_service.create_question(1, q2)
    return [q1_obj.question_id, q2_obj.question_id]

class TestCreatePaper:
    def test_create_valid_paper(self, paper_service, db, setup_questions):
        questions_map = [
            {"question_id": setup_questions[0], "score": 10},
            {"question_id": setup_questions[1], "score": 20}
        ]
        success, msg, paper = paper_service.create_paper(1, "Test Paper", questions_map)
        assert success is True
        assert msg == "Paper created successfully"
        assert paper.total_score == 30
        assert paper.name == "Test Paper"
        assert paper.creator_id == 1

    def test_create_paper_with_invalid_question_id(self, paper_service):
        questions_map = [
            {"question_id": 999, "score": 10}
        ]
        success, msg, paper = paper_service.create_paper(1, "Bad Paper", questions_map)
        assert success is False
        assert "do not exist" in msg

    def test_create_paper_missing_score_field(self, paper_service, setup_questions):
        questions_map = [
            {"question_id": setup_questions[0]}  # Missing score
        ]
        success, msg, paper = paper_service.create_paper(1, "Bad Paper", questions_map)
        assert success is False
        assert "do not exist" in msg  # Validation fails because structure is wrong or ID missing logic handles it

class TestDeletePaper:
    def test_delete_existing_paper(self, paper_service, db, setup_questions):
        questions_map = [{"question_id": setup_questions[0], "score": 10}]
        paper_service.create_paper(1, "Del Me", questions_map)
        success, msg = paper_service.delete_paper(1)
        assert success is True
        assert db.get_paper(1) is None

    def test_delete_nonexistent_paper(self, paper_service):
        success, msg = paper_service.delete_paper(999)
        assert success is False
        assert "Paper not found" in msg

class TestGetByCreator:
    def test_get_papers_by_creator(self, paper_service, db, setup_questions):
        questions_map1 = [{"question_id": setup_questions[0], "score": 10}]
        questions_map2 = [{"question_id": setup_questions[1], "score": 20}]
        paper_service.create_paper(1, "Paper A", questions_map1)
        paper_service.create_paper(1, "Paper B", questions_map2)
        paper_service.create_paper(2, "Paper C", questions_map1) # Different creator
        
        success, msg, papers = paper_service.get_by_creator(1)
        assert success is True
        assert len(papers) == 2
        names = [p.name for p in papers]
        assert "Paper A" in names
        assert "Paper B" in names