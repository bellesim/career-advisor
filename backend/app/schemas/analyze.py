from typing import Optional
from pydantic import BaseModel


class Answer(BaseModel):
    question: str
    answer: str


class QuestionsRequest(BaseModel):
    session_id: str
    resume_id: str
    jd_id: str


class QuestionsResponse(BaseModel):
    questions: list[str]


class AnalyzeRequest(BaseModel):
    session_id: str
    resume_id: str
    jd_id: str
    answers: Optional[list[Answer]] = None


class AnalyzeResponse(BaseModel):
    report_id: str
