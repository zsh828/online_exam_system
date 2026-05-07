import pytest
from src.database import InMemoryDatabase
from src.services import ExamService, StatisticsService, QuestionService, PaperService
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
def exam_service(db):
    return ExamService(db)

@pytest.fixture
def stats_service(db):
    return StatisticsService(db)

@pytest.fixture
def setup_exam_environment(question_service, paper_service):
    # Create Questions
    q1_data = {
        "q_type": "single",
        "content": "What is 1+1?",
        "options": ["1", "2", "3"],
        "correct_answer": "2",
        "category": "math"
    }
    q2_data = {
        "q_type": "true_false",
        "content": "Is earth flat?",
        "options": ["True", "False"],
        "correct_answer": False,
        "category": "geo"
    }
    
    _, _, q1 = question_service.create_question(1, q1_data)
    _, _, q2 = question_service.create_question(1, q2_data)
    
    # Create Paper using the dynamically generated IDs
    questions_map = [
        {"question_id": q1.question_id, "score": 50},
        {"question_id": q2.question_id, "score": 50}
    ]
    _, _, paper = paper_service.create_paper(1, "Simple Exam", questions_map)
    
    return 1, paper.paper_id # user_id, paper_id

class TestSubmitExam:
    def test_submit_complete_correct_answers(self, exam_service, db, setup_exam_environment):
        user_id, paper_id = setup_exam_environment
        answers = [
            {"question_id": 1, "user_answer": "2"},
            {"question_id": 2, "user_answer": False}
        ]
        # Note: The answers above use hardcoded IDs 1 and 2 which might not match the dynamic IDs from setup_exam_environment
        # However, looking at the previous code, it seems the test intended to rely on specific IDs.
        # To make this robust, we should fetch the actual question IDs from the environment or adjust answers.
        # But since setup_exam_environment returns paper_id, and we know the paper structure, 
        # let's look at how other tests handle this. 
        # Actually, the safest way in these isolated tests is to ensure the answers match the paper's question IDs.
        # Since setup_exam_environment creates the paper, we can retrieve the paper to get its question IDs.
        
        # Re-fetching paper to ensure we have the right question IDs for answers
        # This requires access to db or paper_service. Let's modify the test slightly to be robust.
        # However, to keep changes minimal and focused on the failure:
        # The failure was in test_multiple_choice_grading. 
        # Let's fix test_multiple_choice_grading primarily.
        
        # For this test, let's assume the user knows the IDs or we pass them.
        # A better approach for the test itself without changing signature too much:
        # We will rely on the fact that `setup_exam_environment` sets up the DB state.
        # But the answers list has hardcoded IDs. This is fragile.
        # Let's fix the test to be dynamic.
        
        # Get the paper to find out which question IDs were used
        paper = exam_service.db.get_paper(paper_id)
        correct_qids = paper.get_question_ids()
        
        # Map answers to the actual question IDs
        # Assuming order matches for simplicity in this specific test case logic
        # Or better: construct answers based on correct_qids
        answers = []
        # We need to provide answers for all questions in the paper
        # Let's just say we answer everything correctly.
        # We need to know the type of each question to provide correct answer.
        # This is getting complex. Let's stick to the original intent but fix the bug.
        
        # Original test assumed Q1 and Q2 existed with IDs 1 and 2.
        # With dynamic IDs, we must adapt.
        
        # Let's extract question details from the paper's question map by querying the DB
        q1_obj = exam_service.db.get_question(correct_qids[0])
        q2_obj = exam_service.db.get_question(correct_qids[1])
        
        ans1_val = "2" if q1_obj.q_type == 'single' else False # Simplified assumption
        ans2_val = False if q2_obj.q_type == 'true_false' else "2"
        
        answers = [
            {"question_id": correct_qids[0], "user_answer": ans1_val},
            {"question_id": correct_qids[1], "user_answer": ans2_val}
        ]
        
        success, msg, record = exam_service.submit_exam(user_id, paper_id, answers)
        assert success is True
        assert record.score == 100

    def test_submit_incomplete_answers(self, exam_service, setup_exam_environment):
        user_id, paper_id = setup_exam_environment
        paper = exam_service.db.get_paper(paper_id)
        qids = paper.get_question_ids()
        
        # Submit only one answer
        answers = [
            {"question_id": qids[0], "user_answer": "dummy"}
        ]
        success, msg, record = exam_service.submit_exam(user_id, paper_id, answers)
        assert success is False
        assert "Incomplete" in msg

    def test_submit_wrong_answer(self, exam_service, db, setup_exam_environment):
        user_id, paper_id = setup_exam_environment
        paper = exam_service.db.get_paper(paper_id)
        qids = paper.get_question_ids()
        
        q1_obj = exam_service.db.get_question(qids[0])
        q2_obj = exam_service.db.get_question(qids[1])
        
        # Wrong answer for first, correct for second
        ans1_val = "1" # Wrong
        ans2_val = False if q2_obj.q_type == 'true_false' else "2"
        
        answers = [
            {"question_id": qids[0], "user_answer": ans1_val},
            {"question_id": qids[1], "user_answer": ans2_val}
        ]
        success, msg, record = exam_service.submit_exam(user_id, paper_id, answers)
        assert success is True
        # First question is single choice worth 50. If wrong, score is 50.
        assert record.score == 50

    def test_submit_nonexistent_paper(self, exam_service):
        success, msg, record = exam_service.submit_exam(1, 999, [])
        assert success is False
        assert "Paper not found" in msg

    def test_multiple_choice_grading(self, exam_service, db, question_service, paper_service):
        # Setup specific MC question
        mc_data = {
            "q_type": "multiple",
            "content": "Select colors",
            "options": ["Red", "Blue", "Green"],
            "correct_answer": ["Red", "Blue"],
            "category": "art"
        }
        _, _, mc_question = question_service.create_question(1, mc_data)
        
        # Use the ACTUAL ID returned by create_question
        pm = [{"question_id": mc_question.question_id, "score": 100}]
        success, msg, paper = paper_service.create_paper(1, "MC Exam", pm)
        
        # Use the actual paper ID returned by create_paper
        assert success is True, f"Failed to create paper: {msg}"
        paper_id = paper.paper_id
        
        # Submit correct order
        ans1 = [{"question_id": mc_question.question_id, "user_answer": ["Red", "Blue"]}]
        _, _, rec1 = exam_service.submit_exam(1, paper_id, ans1)
        assert rec1.score == 100
        
        # Submit reversed order (should still be correct)
        ans2 = [{"question_id": mc_question.question_id, "user_answer": ["Blue", "Red"]}]
        _, _, rec2 = exam_service.submit_exam(2, paper_id, ans2)
        assert rec2.score == 100

class TestStatistics:
    def test_stats_empty_paper(self, stats_service):
        result = stats_service.analyze_paper(999)
        assert result["average_score"] == 0
        assert result["max_score"] == 0
        assert result["min_score"] == 0
        assert result["pass_rate"] == 0
        assert result["total_students"] == 0

    def test_stats_calculate_avg_max_min(self, exam_service, db, setup_exam_environment, stats_service):
        user_id, paper_id = setup_exam_environment
        paper = exam_service.db.get_paper(paper_id)
        qids = paper.get_question_ids()
        
        q1_obj = exam_service.db.get_question(qids[0])
        q2_obj = exam_service.db.get_question(qids[1])

        # Student 1: 100 points (Correct answers)
        # Determine correct answers based on question types
        c1 = "2" if q1_obj.q_type == 'single' else False
        c2 = False if q2_obj.q_type == 'true_false' else "2"
        
        exam_service.submit_exam(1, paper_id, [
            {"question_id": qids[0], "user_answer": c1},
            {"question_id": qids[1], "user_answer": c2}
        ])
        
        # Student 2: 0 points (Wrong answers)
        w1 = "1" if q1_obj.q_type == 'single' else True
        w2 = True if q2_obj.q_type == 'true_false' else "1"
        
        exam_service.submit_exam(2, paper_id, [
            {"question_id": qids[0], "user_answer": w1},
            {"question_id": qids[1], "user_answer": w2}
        ])
        
        result = stats_service.analyze_paper(paper_id)
        assert result["average_score"] == 50.0
        assert result["max_score"] == 100
        assert result["min_score"] == 0
        assert result["total_students"] == 2
        # Only student 1 passed (>=60)
        assert result["pass_rate"] == 50.0

    def test_stats_pass_rate_boundary(self, exam_service, db, setup_exam_environment, stats_service):
        user_id, paper_id = setup_exam_environment
        paper = exam_service.db.get_paper(paper_id)
        qids = paper.get_question_ids()
        
        q1_obj = exam_service.db.get_question(qids[0])
        q2_obj = exam_service.db.get_question(qids[1])

        c1 = "2" if q1_obj.q_type == 'single' else False
        c2 = False if q2_obj.q_type == 'true_false' else "2"
        
        exam_service.submit_exam(1, paper_id, [
            {"question_id": qids[0], "user_answer": c1},
            {"question_id": qids[1], "user_answer": c2}
        ])
        
        result = stats_service.analyze_paper(paper_id)
        assert result["pass_rate"] == 100.0