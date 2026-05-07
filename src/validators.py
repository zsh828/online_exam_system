import re
from typing import List, Dict, Any


def validate_password(password: str) -> bool:
    """
    Password must be at least 8 characters long and contain both letters and numbers.
    """
    if len(password) < 8:
        return False
    
    has_letter = bool(re.search(r'[a-zA-Z]', password))
    has_digit = bool(re.search(r'\d', password))
    
    return has_letter and has_digit


def validate_question_data(data: Dict[str, Any]) -> bool:
    """
    Basic validation for question creation/update.
    """
    required_fields = ['q_type', 'content', 'options', 'correct_answer', 'category']
    if not all(field in data for field in required_fields):
        return False
    
    valid_types = ['single', 'multiple', 'true_false']
    if data['q_type'] not in valid_types:
        return False
    
    if not isinstance(data['options'], list) or len(data['options']) == 0:
        return False
        
    return True


def validate_paper_questions(paper_questions: List[Dict[str, Any]], available_questions: Dict[int, Any]) -> bool:
    """
    Check if all question IDs in the paper map exist in the database.
    """
    for pq in paper_questions:
        if 'question_id' not in pq or 'score' not in pq:
            return False
        qid = pq['question_id']
        if qid not in available_questions:
            return False
    return True


def validate_exam_submission(submission: List[Dict[str, Any]], required_question_ids: List[int]) -> bool:
    """
    Check if the submission contains answers for all required questions.
    """
    if len(submission) != len(required_question_ids):
        return False
    
    submission_qids = set(item['question_id'] for item in submission)
    required_set = set(required_question_ids)
    
    return submission_qids == required_set