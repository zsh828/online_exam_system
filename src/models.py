import hashlib
import json
import time
from typing import List, Dict, Any, Optional


class User:
    def __init__(self, user_id: int, username: str, password_hash: str, role: str):
        self.user_id = user_id
        self.username = username
        self.password_hash = password_hash
        self.role = role  # 'student' or 'teacher'

    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def check_password(self, password: str) -> bool:
        return self.password_hash == User.hash_password(password)


class Question:
    def __init__(self, question_id: int, q_type: str, content: str, options: List[str], 
                 correct_answer: Any, category: str, created_at: float):
        self.question_id = question_id
        self.q_type = q_type  # 'single', 'multiple', 'true_false'
        self.content = content
        self.options = options
        self.correct_answer = correct_answer
        self.category = category
        self.created_at = created_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            "question_id": self.question_id,
            "q_type": self.q_type,
            "content": self.content,
            "options": self.options,
            "correct_answer": self.correct_answer,
            "category": self.category,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Question':
        return cls(
            question_id=data["question_id"],
            q_type=data["q_type"],
            content=data["content"],
            options=data["options"],
            correct_answer=data["correct_answer"],
            category=data["category"],
            created_at=data["created_at"]
        )


class Paper:
    def __init__(self, paper_id: int, name: str, questions_map: List[Dict[str, Any]], 
                 total_score: int, creator_id: int, created_at: float):
        """
        questions_map: List of dicts with keys 'question_id' and 'score'
        """
        self.paper_id = paper_id
        self.name = name
        self.questions_map = questions_map
        self.total_score = total_score
        self.creator_id = creator_id
        self.created_at = created_at

    def get_question_ids(self) -> List[int]:
        return [qm['question_id'] for qm in self.questions_map]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "paper_id": self.paper_id,
            "name": self.name,
            "questions_map": self.questions_map,
            "total_score": self.total_score,
            "creator_id": self.creator_id,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Paper':
        return cls(
            paper_id=data["paper_id"],
            name=data["name"],
            questions_map=data["questions_map"],
            total_score=data["total_score"],
            creator_id=data["creator_id"],
            created_at=data["created_at"]
        )


class ExamRecord:
    def __init__(self, record_id: int, user_id: int, paper_id: int, answers: List[Dict[str, Any]], 
                 score: int, submitted_at: float):
        """
        answers: List of dicts with keys 'question_id' and 'user_answer'
        """
        self.record_id = record_id
        self.user_id = user_id
        self.paper_id = paper_id
        self.answers = answers
        self.score = score
        self.submitted_at = submitted_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            "record_id": self.record_id,
            "user_id": self.user_id,
            "paper_id": self.paper_id,
            "answers": self.answers,
            "score": self.score,
            "submitted_at": self.submitted_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExamRecord':
        return cls(
            record_id=data["record_id"],
            user_id=data["user_id"],
            paper_id=data["paper_id"],
            answers=data["answers"],
            score=data["score"],
            submitted_at=data["submitted_at"]
        )