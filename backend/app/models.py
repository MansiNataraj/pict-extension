from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class MessageTurn(BaseModel):
    speaker: str
    message: str

# --- Thread Auditor Models ---
class ThreadAnalyseRequest(BaseModel):
    session_id: str = "default-session"
    language_code: str = "hi"
    thread: List[MessageTurn]
    provider: Optional[str] = "auto"

class ThreadAnalyseResponse(BaseModel):
    session_id: str
    health_score: int
    crt_violations: List[str]
    root_cause: str
    remediation_advice: str
    model_used: str

# --- Formality & CRT Coach Models ---
class FormalityVariants(BaseModel):
    formal: str
    semi_formal: str
    casual: str

class CoachRequest(BaseModel):
    session_id: str = "default-session"
    language_code: str = "hi"
    draft_message: str
    recipient_role: Optional[str] = Field(
        default="senior", 
        description="One of: 'senior', 'peer', 'junior'"
    )
    provider: Optional[str] = "auto"

class CoachResponse(BaseModel):
    is_risky: bool
    risk_level: str
    crt_code: Optional[str] = None
    warning_message: Optional[str] = None
    clarification_question: Optional[str] = None
    variants: Optional[FormalityVariants] = None
    predicted_reactions: Optional[Dict[str, str]] = None
    model_used: str

# --- Ghostwriter Reply Models ---
class ReplyRequest(BaseModel):
    session_id: str = "default-session"
    language_code: str = "hi"
    conversation_history: List[MessageTurn]
    goal: str
    provider: Optional[str] = "auto"

class ReplyResponse(BaseModel):
    suggested_reply: str
    diplomatic_rationale: str
    model_used: str

# --- Speech-to-Speech Models ---
class SpeechTranslateRequest(BaseModel):
    session_id: str = "speech-session-default"
    audio_text: str
    source_language: str
    target_language: str
    tone: str = "polite"
    provider: Optional[str] = "auto"

class SpeechTranslateResponse(BaseModel):
    session_id: str
    original_text: str
    translated_text: str
    source_language: str
    target_language: str
    selected_tone: str
    t_v_pronoun_used: str
    cultural_notes: str
    model_used: str

# --- Incoming Chat Reply Models (contact replies to the user) ---
class ChatReplyRequest(BaseModel):
    session_id: str = "default-session"
    language_code: str = "hi"
    contact_name: str
    contact_role: str = Field(
        default="peer",
        description="One of: 'senior', 'peer', 'junior'"
    )
    conversation_history: List[MessageTurn]
    provider: Optional[str] = "auto"

class ChatReplyResponse(BaseModel):
    speaker: str
    reply: str
    model_used: str
