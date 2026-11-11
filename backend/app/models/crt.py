"""Schemas for the select-to-translate CRT flow (used by the browser extension)."""
from typing import List, Optional
from pydantic import BaseModel


class CrtQuestion(BaseModel):
    id: str
    crt_code: str
    question: str
    options: List[str]

class CrtQuestionsRequest(BaseModel):
    text: str
    source_language: str = "auto"   # "auto" or a language code
    target_language: str
    provider: Optional[str] = "auto"

class CrtQuestionsResponse(BaseModel):
    questions: List[CrtQuestion]
    model_used: str

class CrtAnswer(BaseModel):
    id: str
    crt_code: str
    question: str
    answer: str

class CrtTranslateRequest(BaseModel):
    text: str
    source_language: str = "auto"
    target_language: str
    answers: List[CrtAnswer] = []
    provider: Optional[str] = "auto"

class CrtNote(BaseModel):
    code: str
    note: str

class CrtVariant(BaseModel):
    label: str
    text: str
    nuance: str = ""

class CrtTranslateResponse(BaseModel):
    translated_text: str
    register_used: str
    crt_applied: List[CrtNote]
    variants: List[CrtVariant] = []
    cultural_notes: str
    model_used: str
