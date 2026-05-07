import time
from typing import List, Dict, Any, Optional, Tuple
from src.models import User, Question, Paper, ExamRecord
from src.database import InMemoryDatabase
from src.validators import validate_password, validate_question_data, validate_paper_questions, validate_exam_submission


class UserService:
    def __init__(self, db: InMemoryDatabase):
        self.db = db

    def register(self, username: str, password: str, role: str) -> Tuple[bool, str, Optional[User]]:
        if not validate_password(password):
            return False, "Password must be at least 8 characters and contain letters and numbers", None
        
        if self.db.get_user_by_username(username):
            return False, "Username already exists", None
        
        if role not in ['student', 'teacher']:
            return False, "Invalid role", None

        user_id = self.db.generate_next_user_id()
        password_hash = User.hash_password(password)
        user = User(user_id=user_id, username=username, password_hash=password_hash, role=role)
        
        self.db.add_user(user)
        return True, "Registration successful", user

    def login(self, username: str, password: str) -> Tuple[bool, str, Optional[User]]:
        user = self.db.get_user_by_username(username)
        if not user:
            return False, "User not found", None
        
        if not user.check_password(password):
            return False, "Incorrect password", None
            
        return True, "Login successful", user


class QuestionService:
    def __init__(self, db: InMemoryDatabase):
        self.db = db

    def create_question(self, teacher_id: int, data: Dict[str, Any]) -> Tuple[bool, str, Optional[Question]]:
        if not validate_question_data(data):
            return False, "Invalid question data", None
        
        # In a real system, we might verify teacher_id is actually a teacher here
        # For simplicity, we assume the caller checks permissions
        
        question_id = self.db.generate_next_question_id()
        created_at = time.time()
        
        question = Question(
            question_id=question_id,
            q_type=data['q_type'],
            content=data['content'],
            options=data['options'],
            correct_answer=data['correct_answer'],
            category=data['category'],
            created_at=created_at
        )
        
        self.db.add_question(question)
        return True, "Question created successfully", question

    def delete_question(self, question_id: int) -> Tuple[bool, str]:
        try:
            self.db.delete_question(question_id)
            return True, "Question deleted successfully"
        except ValueError as e:
            return False, str(e)

    def update_question(self, question_id: int, data: Dict[str, Any]) -> Tuple[bool, str, Optional[Question]]:
        existing = self.db.get_question(question_id)
        if not existing:
            return False, "Question not found", None
        
        if not validate_question_data(data):
            return False, "Invalid question data", None
        
        updated_question = Question(
            question_id=question_id,
            q_type=data['q_type'],
            content=data['content'],
            options=data['options'],
            correct_answer=data['correct_answer'],
            category=data['category'],
            created_at=existing.created_at  # Keep original creation time
        )
        
        self.db.update_question(updated_question)
        return True, "Question updated successfully", updated_question

    def query_by_category(self, category: str) -> Tuple[bool, str, List[Question]]:
        questions = self.db.get_questions_by_category(category)
        return True, "Query successful", questions


class PaperService:
    def __init__(self, db: InMemoryDatabase):
        self.db = db

    def create_paper(self, creator_id: int, name: str, questions_map: List[Dict[str, Any]]) -> Tuple[bool, str, Optional[Paper]]:
        # Validate that all question IDs exist
        available_qids = {q.question_id for q in self.db.questions.values()}
        if not validate_paper_questions(questions_map, available_qids):
            return False, "One or more question IDs do not exist", None
        
        # Calculate total score
        total_score = sum(qm['score'] for qm in questions_map)
        
        paper_id = self.db.generate_next_paper_id()
        created_at = time.time()
        
        paper = Paper(
            paper_id=paper_id,
            name=name,
            questions_map=questions_map,
            total_score=total_score,
            creator_id=creator_id,
            created_at=created_at
        )
        
        self.db.add_paper(paper)
        return True, "Paper created successfully", paper

    def delete_paper(self, paper_id: int) -> Tuple[bool, str]:
        try:
            self.db.delete_paper(paper_id)
            return True, "Paper deleted successfully"
        except ValueError as e:
            return False, str(e)

    def get_by_creator(self, creator_id: int) -> Tuple[bool, str, List[Paper]]:
        papers = self.db.get_papers_by_creator(creator_id)
        return True, "Query successful", papers

    def get_all_papers(self) -> List[Paper]:
        return list(self.db.papers.values())


class ExamService:
    def __init__(self, db: InMemoryDatabase):
        self.db = db

    def submit_exam(self, user_id: int, paper_id: int, answers: List[Dict[str, Any]]) -> Tuple[bool, str, Optional[ExamRecord]]:
        paper = self.db.get_paper(paper_id)
        if not paper:
            return False, "Paper not found", None
        
        required_qids = paper.get_question_ids()
        
        # Validate submission completeness
        if not validate_exam_submission(answers, required_qids):
            return False, "Incomplete answers provided", None
        
        # Grade the exam
        score = self._grade_exam(paper, answers)
        
        record_id = self.db.generate_next_record_id()
        submitted_at = time.time()
        
        record = ExamRecord(
            record_id=record_id,
            user_id=user_id,
            paper_id=paper_id,
            answers=answers,
            score=score,
            submitted_at=submitted_at
        )
        
        self.db.add_record(record)
        return True, "Exam submitted successfully", record

    def _grade_exam(self, paper: Paper, answers: List[Dict[str, Any]]) -> int:
        score = 0
        # Create a map for quick lookup of user answers
        answer_map = {ans['question_id']: ans['user_answer'] for ans in answers}
        
        for qm in paper.questions_map:
            qid = qm['question_id']
            score_value = qm['score']
            
            question = self.db.get_question(qid)
            if not question:
                continue
                
            user_ans = answer_map.get(qid)
            correct_ans = question.correct_answer
            
            if self._check_answer_correct(question.q_type, user_ans, correct_ans):
                score += score_value
                
        return score

    def _check_answer_correct(self, q_type: str, user_ans: Any, correct_ans: Any) -> bool:
        if q_type == 'single':
            return user_ans == correct_ans
        elif q_type == 'true_false':
            # Normalize boolean/string representations
            if isinstance(correct_ans, bool):
                return bool(user_ans) == correct_ans
            else:
                return str(user_ans).lower() == str(correct_ans).lower()
        elif q_type == 'multiple':
            # Assume lists are sorted for comparison
            if not isinstance(user_ans, list) or not isinstance(correct_ans, list):
                return False
            return sorted(user_ans) == sorted(correct_ans)
        return False

    def get_user_records(self, user_id: int) -> List[ExamRecord]:
        return self.db.get_records_by_user(user_id)

    def get_paper_records(self, paper_id: int) -> List[ExamRecord]:
        return self.db.get_records_by_paper(paper_id)


class StatisticsService:
    def __init__(self, db: InMemoryDatabase):
        self.db = db

    def analyze_paper(self, paper_id: int) -> Dict[str, Any]:
        records = self.db.get_records_by_paper(paper_id)
        
        if not records:
            return {
                "paper_id": paper_id,
                "average_score": 0,
                "max_score": 0,
                "min_score": 0,
                "pass_rate": 0,
                "total_students": 0
            }
        
        scores = [r.score for r in records]
        total_students = len(scores)
        avg_score = sum(scores) / total_students
        max_score = max(scores)
        min_score = min(scores)
        
        # Pass rate >= 60
        passed_count = sum(1 for s in scores if s >= 60)
        pass_rate = (passed_count / total_students) * 100
        
        return {
            "paper_id": paper_id,
            "average_score": round(avg_score, 2),
            "max_score": max_score,
            "min_score": min_score,
            "pass_rate": round(pass_rate, 2),
            "total_students": total_students
        }