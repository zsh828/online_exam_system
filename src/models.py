import hashlib
import time
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple


@dataclass
class User:
    user_id: int
    username: str
    password_hash: str
    role: str  # 'student' or 'teacher'

    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode('utf-8')).hexdigest()


@dataclass
class Question:
    question_id: int
    q_type: str  # 'single', 'multiple', 'judge'
    content: str
    options: List[str]
    correct_answer: any  # str for single/judge, list[str] for multiple
    category: str


@dataclass
class ExamPaper:
    paper_id: int
    name: str
    questions: List[Tuple[int, float]]  # List of (question_id, score)
    total_score: float
    creator_id: int


@dataclass
class ExamRecord:
    record_id: int
    user_id: int
    paper_id: int
    answers: Dict[int, any]  # question_id -> answer
    score: float
    submit_time: float