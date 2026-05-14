import pytest
from src.database import InMemoryDatabase
from src.services import AuthService, QuestionService, PaperService, ExamService


@pytest.fixture
def full_setup():
    db = InMemoryDatabase()
    auth = AuthService(db)
    qs = QuestionService(db)
    ps = PaperService(db)
    es = ExamService(db)
    
    # Create users
    auth.register("t1", "pwd123", "teacher")
    auth.register("s1", "pwd123", "student")
    auth.register("s2", "pwd123", "student")
    
    t1 = db.get_user_by_username("t1")
    s1 = db.get_user_by_username("s1")
    s2 = db.get_user_by_username("s2")
    
    # Add Questions
    q1_res = qs.add_question(t1.user_id, "single", "Q1", ["A", "B"], "A", "Gen")
    q2_res = qs.add_question(t1.user_id, "judge", "Q2", ["T", "F"], "T", "Gen")
    q3_res = qs.add_question(t1.user_id, "multiple", "Q3", ["A", "B", "C"], ["A", "C"], "Gen")
    
    q1_id = q1_res["question_id"]
    q2_id = q2_res["question_id"]
    q3_id = q3_res["question_id"]
    
    return db, auth, qs, ps, es, t1, s1, s2, q1_id, q2_id, q3_id

def test_create_paper_success(full_setup):
    db, auth, qs, ps, es, t1, s1, s2, q1_id, q2_id, q3_id = full_setup
    questions = [(q1_id, 10.0), (q2_id, 20.0)]
    result = ps.create_paper(t1.user_id, "Test Paper 1", questions)
    
    assert result["success"] is True
    assert "paper_id" in result
    paper = db.get_paper(result["paper_id"])
    assert paper.total_score == 30.0

def test_create_paper_invalid_question_id(full_setup):
    db, auth, qs, ps, es, t1, s1, s2, q1_id, q2_id, q3_id = full_setup
    questions = [(9999, 10.0)] # Non-existent ID
    result = ps.create_paper(t1.user_id, "Bad Paper", questions)
    
    assert result["success"] is False
    assert "do not exist" in result["message"]

def test_submit_exam_and_scoring(full_setup):
    db, auth, qs, ps, es, t1, s1, s2, q1_id, q2_id, q3_id = full_setup
    
    # Create Paper with 2 questions: Q1 (10pts), Q2 (20pts)
    p_res = ps.create_paper(t1.user_id, "Exam 1", [(q1_id, 10.0), (q2_id, 20.0)])
    paper_id = p_res["paper_id"]
    
    # Student submits: Q1 Correct (A), Q2 Wrong (F)
    answers = {
        q1_id: "A",
        q2_id: "F"
    }
    
    submit_res = es.submit_exam(s1.user_id, paper_id, answers)
    assert submit_res["success"] is True
    assert submit_res["score"] == 10.0 # Only Q1 correct

def test_submit_exam_multiple_choice(full_setup):
    db, auth, qs, ps, es, t1, s1, s2, q1_id, q2_id, q3_id = full_setup
    
    # Paper with Q3 (Multiple, 30pts). Correct: ["A", "C"]
    p_res = ps.create_paper(t1.user_id, "Exam Multi", [(q3_id, 30.0)])
    paper_id = p_res["paper_id"]
    
    # Correct submission
    answers_correct = {q3_id: ["A", "C"]}
    res_correct = es.submit_exam(s1.user_id, paper_id, answers_correct)
    assert res_correct["score"] == 30.0
    
    # Partial/Wrong submission (Order shouldn't matter if logic is correct, but exact match required for list)
    # My implementation sorts them.
    answers_wrong_order = {q3_id: ["C", "A"]}
    res_order = es.submit_exam(s2.user_id, paper_id, answers_wrong_order)
    assert res_order["score"] == 30.0

def test_get_statistics(full_setup):
    db, auth, qs, ps, es, t1, s1, s2, q1_id, q2_id, q3_id = full_setup
    
    # Paper: Q1 (10pts), Q2 (20pts). Total 30. Pass >= 60%? No, requirement says >=60 points.
    # Let's make scores higher to test pass rate easily.
    # Redefine paper with higher scores: Q1 (60pts), Q2 (40pts). Total 100.
    p_res = ps.create_paper(t1.user_id, "Stats Exam", [(q1_id, 60.0), (q2_id, 40.0)])
    paper_id = p_res["paper_id"]
    
    # S1 gets 100 (Pass)
    es.submit_exam(s1.user_id, paper_id, {q1_id: "A", q2_id: "T"})
    
    # S2 gets 60 (Pass)
    es.submit_exam(s2.user_id, paper_id, {q1_id: "A", q2_id: "F"}) # Q1 correct=60, Q2 wrong=0. Total 60.
    
    stats = es.get_statistics(t1.user_id, paper_id)
    assert stats["success"] is True
    assert stats["avg_score"] == 80.0
    assert stats["max_score"] == 100.0
    assert stats["min_score"] == 60.0
    assert stats["pass_rate"] == 100.0

def test_query_student_records(full_setup):
    db, auth, qs, ps, es, t1, s1, s2, q1_id, q2_id, q3_id = full_setup
    
    p_res = ps.create_paper(t1.user_id, "Rec Exam", [(q1_id, 10.0)])
    paper_id = p_res["paper_id"]
    
    es.submit_exam(s1.user_id, paper_id, {q1_id: "A"})
    es.submit_exam(s1.user_id, paper_id, {q1_id: "B"}) # Second attempt
    
    records = es.get_student_records(s1.user_id)
    assert len(records) == 2

def test_query_teacher_paper_records(full_setup):
    db, auth, qs, ps, es, t1, s1, s2, q1_id, q2_id, q3_id = full_setup
    
    p_res = ps.create_paper(t1.user_id, "Rec Exam 2", [(q1_id, 10.0)])
    paper_id = p_res["paper_id"]
    
    es.submit_exam(s1.user_id, paper_id, {q1_id: "A"})
    es.submit_exam(s2.user_id, paper_id, {q1_id: "B"})
    
    res = es.get_paper_records(t1.user_id, paper_id)
    assert res["success"] is True
    assert len(res["records"]) == 2