import re
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime


class QuestionSource(BaseModel):
    name: Optional[str] = "Unknown"
    page: Optional[Union[int, str]] = None


class QuestionModel(BaseModel):
    id: str
    question: str
    options: Dict[str, str]
    correct_answer: str
    explanation: Optional[str] = None
    subject: str
    topic: str
    subtopic: str
    difficulty: str
    source: Optional[QuestionSource] = Field(default_factory=QuestionSource)
    tags: List[str] = Field(default_factory=list)
    verified: bool = False
    created_at: Optional[str] = None

    @field_validator("question")
    @classmethod
    def validate_question_text(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Question text cannot be empty or whitespace only.")
        return v.strip()

    @field_validator("options")
    @classmethod
    def validate_options(cls, v: Dict[str, str]) -> Dict[str, str]:
        if not isinstance(v, dict):
            raise ValueError("Options must be a key-value dictionary.")
        clean_opts = {k.strip().upper(): str(val).strip() for k, val in v.items()}
        required_keys = {"A", "B", "C", "D"}
        if set(clean_opts.keys()) != required_keys:
            raise ValueError(f"Options must contain exactly keys A, B, C, and D. Got: {list(clean_opts.keys())}")
        for k in required_keys:
            if not clean_opts[k]:
                raise ValueError(f"Option {k} cannot be empty.")
        return clean_opts

    @field_validator("correct_answer")
    @classmethod
    def validate_correct_answer(cls, v: str) -> str:
        clean = v.strip().upper() if isinstance(v, str) else ""
        if clean not in {"A", "B", "C", "D"}:
            raise ValueError(f"Correct answer must be one of 'A', 'B', 'C', 'D'. Got: '{v}'")
        return clean

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, v: str) -> str:
        clean = v.strip().lower() if isinstance(v, str) else ""
        if clean not in {"easy", "medium", "hard"}:
            raise ValueError(f"Difficulty must be 'easy', 'medium', or 'hard'. Got: '{v}'")
        return clean

    @field_validator("subject", "topic", "subtopic")
    @classmethod
    def validate_hierarchy(cls, v: str, info) -> str:
        if not v or not str(v).strip():
            raise ValueError(f"{info.field_name.capitalize()} cannot be empty.")
        return str(v).strip()

    @model_validator(mode="after")
    def validate_verified_explanation(self):
        if self.verified:
            if not self.explanation or not self.explanation.strip():
                raise ValueError("Verified questions must have a non-empty explanation.")
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()
        return self


class ImportResult(BaseModel):
    batch_id: str
    total_read: int = 0
    imported: int = 0
    rejected: int = 0
    exact_duplicates: int = 0
    probable_duplicates: int = 0
    flagged: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []


class SessionStartRequest(BaseModel):
    session_type: str = "daily_mixed" # 'daily_mixed', 'subject', 'topic', 'subtopic', 'weak_topic', 'revision_only', 'incorrect_only', 'timed', 'full_mock'
    size: int = 20
    subject_id: Optional[int] = None
    topic_id: Optional[int] = None
    subtopic_id: Optional[int] = None
    difficulty: Optional[str] = None # 'easy', 'medium', 'hard' or None
    time_limit_minutes: Optional[int] = None


class SubmitAnswerRequest(BaseModel):
    session_id: str
    question_id: str
    selected_option: Optional[str] = None # 'A', 'B', 'C', 'D' or None
    time_spent_seconds: int = 0
    is_marked_for_review: bool = False
    confidence: Optional[str] = None # 'low', 'medium', 'high'
    mistake_category: Optional[str] = None # 'concept', 'formula', 'calculation', 'misread', 'guess', 'time', 'other'


class CompleteSessionRequest(BaseModel):
    session_id: str
    time_taken_seconds: int = 0


class SettingsUpdateRequest(BaseModel):
    settings: Dict[str, str]
