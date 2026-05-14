import pytest
from src.database import InMemoryDatabase
from src.services import AuthService, QuestionService, PaperService, ExamService


@pytest.fixture
def setup_env():
    db = InMemoryDatabase()
    auth = AuthService(db)
    qs = QuestionService(db)
    ps = PaperService(db)
    es = ExamService(db)
    
    # Create teacher and student
    auth.register("teacher1", "password123", "teacher")
    auth.register("student1", "password123", "student")
    
    teacher = db.get_user_by_username("teacher1")
    student = db.get_user_by_username("student1")
    
    # Add a question
    q_res = qs.add_question(teacher.user_id, "single", "1+1=?", ["1", "2"], "2", "Math")
    q_id = q_res["question_id"]
    
    # Create a paper
    p_res = ps.create_paper(teacher.user_id, "Math Test", [(q_id, 100.0)])
    p_id = p_res["paper_id"]
    
    return db, es, teacher, student, p_id, q_id

def test_exam_submit_and_statistics(setup_env):
    db, es, teacher, student, p_id, q_id = setup_env
    
    # Submit exam
    submit_res = es.submit_exam(student.user_id, p_id, {q_id: "2"})
    assert submit_res["success"] is True
    assert submit_res["score"] == 100.0
    
    # Get statistics
    stats = es.get_statistics(teacher.user_id, p_id)
    assert stats["success"] is True
    assert stats["avg_score"] == 100.0
    assert stats["max_score"] == 100.0
    assert stats["min_score"] == 100.0
    assert stats["pass_rate"] == 100.0

def test_exam_statistics_empty(setup_env):
    db, es, teacher, student, p_id, q_id = setup_env
    
    # Create a new paper with no submissions
    auth = AuthService(db)
    auth.register("teacher2", "password123", "teacher")
    t2 = db.get_user_by_username("teacher2")
    qs = QuestionService(db)
    ps = PaperService(db)
    
    q_res = qs.add_question(t2.user_id, "judge", "True?", ["T", "F"], "T", "Logic")
    p_res = ps.create_paper(t2.user_id, "Empty Test", [(q_res["question_id"], 50.0)])
    
    stats = es.get_statistics(t2.user_id, p_res["paper_id"])
    assert stats["success"] is True
    assert stats["avg_score"] == 0