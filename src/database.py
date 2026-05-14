import time
from typing import List, Dict, Optional, Tuple
from src.models import User, Question, ExamPaper, ExamRecord


class InMemoryDatabase:
    def __init__(self):
        self.users: Dict[int, User] = {}
        self.questions: Dict[int, Question] = {}
        self.papers: Dict[int, ExamPaper] = {}
        self.records: Dict[int, ExamRecord] = {}
        
        # Counters for IDs
        self._user_id_counter = 0
        self._question_id_counter = 0
        self._paper_id_counter = 0
        self._record_id_counter = 0

    def add_user(self, username: str, password_hash: str, role: str) -> int:
        self._user_id_counter += 1
        user_id = self._user_id_counter
        user = User(user_id=user_id, username=username, password_hash=password_hash, role=role)
        self.users[user_id] = user
        return user_id

    def get_user_by_username(self, username: str) -> Optional[User]:
        for user in self.users.values():
            if user.username == username:
                return user
        return None

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.users.get(user_id)

    def add_question(self, q_type: str, content: str, options: List[str], correct_answer: any, category: str) -> int:
        self._question_id_counter += 1
        q_id = self._question_id_counter
        question = Question(
            question_id=q_id,
            q_type=q_type,
            content=content,
            options=options,
            correct_answer=correct_answer,
            category=category
        )
        self.questions[q_id] = question
        return q_id

    def get_question(self, question_id: int) -> Optional[Question]:
        return self.questions.get(question_id)

    def delete_question(self, question_id: int) -> bool:
        if question_id in self.questions:
            del self.questions[question_id]
            return True
        return False

    def update_question(self, question_id: int, **kwargs) -> bool:
        if question_id not in self.questions:
            return False
        q = self.questions[question_id]
        for key, value in kwargs.items():
            if hasattr(q, key):
                setattr(q, key, value)
        return True

    def list_questions_by_category(self, category: str) -> List[Question]:
        return [q for q in self.questions.values() if q.category == category]

    def add_paper(self, name: str, questions: List[Tuple[int, float]], creator_id: int) -> Optional[int]:
        # Validate question IDs exist
        for q_id, _ in questions:
            if q_id not in self.questions:
                return None
        
        total_score = sum(score for _, score in questions)
        self._paper_id_counter += 1
        p_id = self._paper_id_counter
        paper = ExamPaper(
            paper_id=p_id,
            name=name,
            questions=questions,
            total_score=total_score,
            creator_id=creator_id
        )
        self.papers[p_id] = paper
        return p_id

    def get_paper(self, paper_id: int) -> Optional[ExamPaper]:
        return self.papers.get(paper_id)

    def delete_paper(self, paper_id: int) -> bool:
        if paper_id in self.papers:
            del self.papers[paper_id]
            return True
        return False

    def add_record(self, user_id: int, paper_id: int, answers: Dict[int, any], score: float) -> int:
        self._record_id_counter += 1
        r_id = self._record_id_counter
        record = ExamRecord(
            record_id=r_id,
            user_id=user_id,
            paper_id=paper_id,
            answers=answers,
            score=score,
            submit_time=time.time()
        )
        self.records[r_id] = record
        return r_id

    def get_records_by_user(self, user_id: int) -> List[ExamRecord]:
        return [r for r in self.records.values() if r.user_id == user_id]

    def get_records_by_paper(self, paper_id: int) -> List[ExamRecord]:
        return [r for r in self.records.values() if r.paper_id == paper_id]