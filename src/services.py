from typing import List, Dict, Optional, Tuple
from src.database import InMemoryDatabase
from src.models import User, Question, ExamPaper, ExamRecord


class AuthService:
    def __init__(self, db: InMemoryDatabase):
        self.db = db

    def register(self, username: str, password: str, role: str) -> Dict:
        if role not in ['student', 'teacher']:
            return {"success": False, "message": "Invalid role"}
        
        if self.db.get_user_by_username(username):
            return {"success": False, "message": "Username already exists"}
        
        if not password or len(password) < 6:
            return {"success": False, "message": "Password must be at least 6 characters"}

        password_hash = User.hash_password(password)
        user_id = self.db.add_user(username, password_hash, role)
        return {"success": True, "user_id": user_id}

    def login(self, username: str, password: str) -> Dict:
        user = self.db.get_user_by_username(username)
        if not user:
            return {"success": False, "message": "Invalid username or password"}
        
        if user.password_hash != User.hash_password(password):
            return {"success": False, "message": "Invalid username or password"}
        
        return {"success": True, "user_id": user.user_id, "role": user.role}


class QuestionService:
    def __init__(self, db: InMemoryDatabase):
        self.db = db

    def add_question(self, teacher_id: int, q_type: str, content: str, options: List[str], correct_answer: any, category: str) -> Dict:
        teacher = self.db.get_user_by_id(teacher_id)
        if not teacher or teacher.role != 'teacher':
            return {"success": False, "message": "Permission denied"}
        
        # Basic validation
        if q_type not in ['single', 'multiple', 'judge']:
            return {"success": False, "message": "Invalid question type"}
        
        q_id = self.db.add_question(q_type, content, options, correct_answer, category)
        return {"success": True, "question_id": q_id}

    def delete_question(self, teacher_id: int, question_id: int) -> Dict:
        teacher = self.db.get_user_by_id(teacher_id)
        if not teacher or teacher.role != 'teacher':
            return {"success": False, "message": "Permission denied"}
        
        success = self.db.delete_question(question_id)
        if success:
            return {"success": True}
        else:
            return {"success": False, "message": "Question not found"}

    def update_question(self, teacher_id: int, question_id: int, **kwargs) -> Dict:
        teacher = self.db.get_user_by_id(teacher_id)
        if not teacher or teacher.role != 'teacher':
            return {"success": False, "message": "Permission denied"}
        
        success = self.db.update_question(question_id, **kwargs)
        if success:
            return {"success": True}
        else:
            return {"success": False, "message": "Question not found"}

    def get_questions_by_category(self, category: str) -> List[Question]:
        return self.db.list_questions_by_category(category)


class PaperService:
    def __init__(self, db: InMemoryDatabase):
        self.db = db

    def create_paper(self, teacher_id: int, name: str, questions: List[Tuple[int, float]]) -> Dict:
        teacher = self.db.get_user_by_id(teacher_id)
        if not teacher or teacher.role != 'teacher':
            return {"success": False, "message": "Permission denied"}
        
        if not questions:
            return {"success": False, "message": "Paper must have at least one question"}

        paper_id = self.db.add_paper(name, questions, teacher_id)
        if paper_id is None:
            return {"success": False, "message": "One or more question IDs do not exist"}
        
        return {"success": True, "paper_id": paper_id}

    def delete_paper(self, teacher_id: int, paper_id: int) -> Dict:
        teacher = self.db.get_user_by_id(teacher_id)
        if not teacher or teacher.role != 'teacher':
            return {"success": False, "message": "Permission denied"}
        
        # Check if paper exists and optionally check ownership if required, 
        # but requirement just says "Teacher can delete". 
        # Usually teachers delete their own, but let's assume any teacher can delete for simplicity 
        # or strictly own. Let's stick to simple permission check + existence.
        paper = self.db.get_paper(paper_id)
        if not paper:
            return {"success": False, "message": "Paper not found"}
            
        # Optional: Enforce only creator can delete? 
        # Requirement: "试卷管理（仅教师）... 删除试卷". Doesn't explicitly say "own".
        # However, standard practice is own. Let's allow any teacher to delete for now as per loose interpretation,
        # or better, check if it's good practice. Let's assume any authenticated teacher can manage papers.
        
        success = self.db.delete_paper(paper_id)
        if success:
            return {"success": True}
        return {"success": False, "message": "Failed to delete"}

    def get_all_papers(self) -> List[ExamPaper]:
        return list(self.db.papers.values())


class ExamService:
    def __init__(self, db: InMemoryDatabase):
        self.db = db

    def submit_exam(self, student_id: int, paper_id: int, answers: Dict[int, any]) -> Dict:
        student = self.db.get_user_by_id(student_id)
        if not student or student.role != 'student':
            return {"success": False, "message": "Permission denied"}
        
        paper = self.db.get_paper(paper_id)
        if not paper:
            return {"success": False, "message": "Paper not found"}
        
        # Calculate Score
        total_score = 0
        for q_id, q_score in paper.questions:
            user_ans = answers.get(q_id)
            if user_ans is None:
                continue
            
            question = self.db.get_question(q_id)
            if not question:
                continue # Should not happen if paper creation was validated
            
            is_correct = False
            if question.q_type == 'multiple':
                # Sort both lists to compare
                if isinstance(user_ans, list) and isinstance(question.correct_answer, list):
                    if sorted(user_ans) == sorted(question.correct_answer):
                        is_correct = True
            else:
                if user_ans == question.correct_answer:
                    is_correct = True
            
            if is_correct:
                total_score += q_score
        
        # Normalize score if needed? No, just sum.
        # But wait, total_score in paper is max score.
        # The calculated total_score is the student's score.
        
        record_id = self.db.add_record(student_id, paper_id, answers, total_score)
        
        return {
            "success": True, 
            "record_id": record_id, 
            "score": total_score,
            "max_score": paper.total_score
        }

    def get_student_records(self, student_id: int) -> List[ExamRecord]:
        return self.db.get_records_by_user(student_id)

    def get_paper_records(self, teacher_id: int, paper_id: int) -> Dict:
        teacher = self.db.get_user_by_id(teacher_id)
        if not teacher or teacher.role != 'teacher':
            return {"success": False, "message": "Permission denied"}
        
        paper = self.db.get_paper(paper_id)
        if not paper:
            return {"success": False, "message": "Paper not found"}
            
        records = self.db.get_records_by_paper(paper_id)
        return {"success": True, "records": records}

    def get_statistics(self, teacher_id: int, paper_id: int) -> Dict:
        res = self.get_paper_records(teacher_id, paper_id)
        if not res["success"]:
            return res
        
        records = res["records"]
        if not records:
            return {
                "success": True,
                "avg_score": 0,
                "max_score": 0,
                "min_score": 0,
                "pass_rate": 0.0
            }
        
        scores = [r.score for r in records]
        avg_score = sum(scores) / len(scores)
        max_score = max(scores)
        min_score = min(scores)
        pass_count = sum(1 for s in scores if s >= 60)
        pass_rate = (pass_count / len(scores)) * 100
        
        return {
            "success": True,
            "avg_score": round(avg_score, 2),
            "max_score": max_score,
            "min_score": min_score,
            "pass_rate": round(pass_rate, 2)
        }