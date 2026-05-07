import copy
from src.models import User, Question, Paper, ExamRecord


class InMemoryDatabase:
    def __init__(self):
        self.users: Dict[int, User] = {}
        self.questions: Dict[int, Question] = {}
        self.papers: Dict[int, Paper] = {}
        self.records: Dict[int, ExamRecord] = {}
        
        # Counters for auto-increment IDs
        self.next_user_id = 1
        self.next_question_id = 1
        self.next_paper_id = 1
        self.next_record_id = 1

    def add_user(self, user: User):
        if user.user_id in self.users:
            raise ValueError("User ID already exists")
        self.users[user.user_id] = user

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.users.get(user_id)

    def get_user_by_username(self, username: str) -> Optional[User]:
        for user in self.users.values():
            if user.username == username:
                return user
        return None

    def delete_user(self, user_id: int):
        if user_id in self.users:
            del self.users[user_id]

    def add_question(self, question: Question):
        if question.question_id in self.questions:
            raise ValueError("Question ID already exists")
        self.questions[question.question_id] = question

    def get_question(self, question_id: int) -> Optional[Question]:
        return self.questions.get(question_id)

    def update_question(self, question: Question):
        if question.question_id not in self.questions:
            raise ValueError("Question not found")
        self.questions[question.question_id] = question

    def delete_question(self, question_id: int):
        if question_id not in self.questions:
            raise ValueError("Question not found")
        del self.questions[question_id]

    def get_questions_by_category(self, category: str) -> List[Question]:
        return [q for q in self.questions.values() if q.category == category]

    def add_paper(self, paper: Paper):
        if paper.paper_id in self.papers:
            raise ValueError("Paper ID already exists")
        self.papers[paper.paper_id] = paper

    def get_paper(self, paper_id: int) -> Optional[Paper]:
        return self.papers.get(paper_id)

    def delete_paper(self, paper_id: int):
        if paper_id not in self.papers:
            raise ValueError("Paper not found")
        del self.papers[paper_id]

    def get_papers_by_creator(self, creator_id: int) -> List[Paper]:
        return [p for p in self.papers.values() if p.creator_id == creator_id]

    def add_record(self, record: ExamRecord):
        if record.record_id in self.records:
            raise ValueError("Record ID already exists")
        self.records[record.record_id] = record

    def get_record(self, record_id: int) -> Optional[ExamRecord]:
        return self.records.get(record_id)

    def get_records_by_user(self, user_id: int) -> List[ExamRecord]:
        return [r for r in self.records.values() if r.user_id == user_id]

    def get_records_by_paper(self, paper_id: int) -> List[ExamRecord]:
        return [r for r in self.records.values() if r.paper_id == paper_id]

    def generate_next_user_id(self) -> int:
        uid = self.next_user_id
        self.next_user_id += 1
        return uid

    def generate_next_question_id(self) -> int:
        qid = self.next_question_id
        self.next_question_id += 1
        return qid

    def generate_next_paper_id(self) -> int:
        pid = self.next_paper_id
        self.next_paper_id += 1
        return pid

    def generate_next_record_id(self) -> int:
        rid = self.next_record_id
        self.next_record_id += 1
        return rid