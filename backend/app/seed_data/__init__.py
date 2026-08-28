"""Seed data aggregator.

The question bank is static/preloaded — no AI anywhere. Questions are
expert-level, categorized by subject, topic, difficulty (hard / very_hard /
expert) and minimum teaching experience (experience_min). To add hundreds of
questions later, append dicts to the per-subject modules.

Question dict shape:
    {
        "subject": "<SUBJECT CODE>",
        "topic": "<TOPIC NAME>",
        "difficulty": "hard" | "very_hard" | "expert",
        "experience_min": int,            # min teaching years to see this question
        "type": "single" | "multiple" | "assertion_reason" | "scenario"
                | "code" | "numerical" | "debugging",
        "text": "question text",
        "options": ["A", "B", "C", "D"],
        "answer": [i, ...],               # 0-based indices of correct options
        "explanation": "why",
    }
"""
from .subjects import SUBJECTS
from .questions_ds_os import QUESTIONS as Q1
from .questions_dbms_cn import QUESTIONS as Q2
from .questions_java_se import QUESTIONS as Q3
from .questions_ml_py_web import QUESTIONS as Q4
from .questions_co_algo import QUESTIONS as Q5
from .questions_extra import QUESTIONS as Q6
from .questions_ai import QUESTIONS as Q7

QUESTION_BANK = Q1 + Q2 + Q3 + Q4 + Q5 + Q6 + Q7

__all__ = ["SUBJECTS", "QUESTION_BANK"]
