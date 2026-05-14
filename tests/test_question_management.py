import pytest
from src.database import InMemoryDatabase
from src.services import AuthService, QuestionService


@pytest.fixture
def setup_data():
    db = InMemoryDatabase()
    auth = AuthService(db)
    qs = QuestionService(db)
    
    # Create a teacher
    auth.register("teacher1", "password123", "teacher")
    teacher = db.get_user_by_username("teacher1")
    
    # Create a student
    auth.register("student1", "password123", "student")
    student = db.get_user_by_username("student1")
    
    return db, auth, qs, teacher, student

def test_add_question_success(setup_data):
    db, auth, qs, teacher, student = setup_data
    result = qs.add_question(
        teacher.user_id, 
        "single", 
        "What is 1+1?", 
        ["1", "2", "3"], 
        "2", 
        "Math"
    )
    assert result["success"] is True
    assert "question_id" in result

def test_add_question_permission_denied(setup_data):
    db, auth, qs, teacher, student = setup_data
    result = qs.add_question(
        student.user_id, 
        "single", 
        "What is 1+1?", 
        ["1", "2", "3"], 
        "2", 
        "Math"
    )
    assert result["success"] is False
    assert "Permission denied" in result["message"]

def test_delete_question_success(setup_data):
    db, auth, qs, teacher, student = setup_data
    add_res = qs.add_question(teacher.user_id, "judge", "True?", ["True", "False"], "True", "Logic")
    q_id = add_res["question_id"]
    
    del_res = qs.delete_question(teacher.user_id, q_id)
    assert del_res["success"] is True
    
    # Verify deletion
    assert db.get_question(q_id) is None

def test_update_question_success(setup_data):
    db, auth, qs, teacher, student = setup_data
    add_res = qs.add_question(teacher.user_id, "single", "Old Q", ["A", "B"], "A", "Cat1")
    q_id = add_res["question_id"]
    
    update_res = qs.update_question(teacher.user_id, q_id, content="New Q", category="Cat2")
    assert update_res["success"] is True
    
    updated_q = db.get_question(q_id)
    assert updated_q.content == "New Q"
    assert updated_q.category == "Cat2"

def test_list_questions_by_category(setup_data):
    db, auth, qs, teacher, student = setup_data
    qs.add_question(teacher.user_id, "single", "Q1", ["A", "B"], "A", "Math")
    qs.add_question(teacher.user_id, "single", "Q2", ["A", "B"], "A", "English")
    qs.add_question(teacher.user_id, "single", "Q3", ["A", "B"], "A", "Math")
    
    math_qs = qs.get_questions_by_category("Math")
    assert len(math_qs) == 2