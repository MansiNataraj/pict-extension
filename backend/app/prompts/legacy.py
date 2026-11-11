from typing import List
from app.models import MessageTurn

def get_thread_analysis_prompt(language: str, thread: List[MessageTurn]) -> str:
    transcript = "\n".join([f"{t.speaker}: {t.message}" for t in thread])
    return f"""You are a sociopragmatic intercultural communication diagnostic engine.
Language: {language}

Conversation Transcript:
{transcript}

Diagnose this thread for pragmatic tension, relational strain, and Cultural Risk Taxonomy (CRT C1-C5) violations:
C1: Register/Honorific Mismatch (T-V distinction)
C2: Idiomatic Opacity
C3: Gender Agreement Discordance
C4: Hierarchy Violation
C5: Cultural/Religious Taboo

Return ONLY a raw JSON object:
{{
  "health_score": 75,
  "crt_violations": ["C1", "C4"],
  "root_cause": "Concise summary of friction",
  "remediation_advice": "Actionable recommendation to repair relational tone"
}}"""

def get_coaching_prompt(language: str, draft: str, recipient_role: str) -> str:
    return f"""You are an expert cross-cultural pragmatic linguistic coach for workplace and interpersonal messaging.
Target Language: {language}
Recipient Role: {recipient_role} (Options: 'senior' / superior, 'peer' / colleague, 'junior' / subordinate)
Draft Message: "{draft}"

Task:
1. Determine if this draft contains any Cultural Risk Taxonomy (CRT) violations given the recipient's role:
   - C1: Register / Pronoun mismatch (e.g., using informal 'Tu/Tum' or 'Nee' with a senior, or overly stiff honorifics with an intimate peer)
   - C2: Idiomatic opacity / mistranslations
   - C3: Gendered concord errors
   - C4: Hierarchy / deference violations
   - C5: Socio-cultural or religious insensitivity

2. Generate THREE calibrated versions of the draft in {language}:
   - Formal: High deference with formal honorific pronouns (e.g. Hindi: Aap, Tamil: Neenga, Kannada: Neevu, Arabic: Hadratak). Suitable for seniors, superiors, elders, or clients.
   - Semi-Formal: Polite, balanced register suitable for professional peer-to-peer collaboration.
   - Casual: Informal, direct peer/colloquial phrasing (e.g. Hindi: Tum/Tu, Tamil: Nee, Kannada: Neenu, Arabic: Inta) suitable for junior teammates or close friends.

3. Provide brief 1-sentence descriptions of how the recipient will perceive each version.

Return ONLY a single valid raw JSON object matching this schema:
{{
  "is_risky": true,
  "risk_level": "amber",
  "crt_code": "C1",
  "warning_message": "Concise 1-sentence warning diagnosing the pragmatic risk in the draft relative to the recipient role",
  "clarification_question": "Optional 1-sentence prompt asking to clarify relationship context if ambiguous",
  "variants": {{
    "formal": "Formal high-deference version in target script",
    "semi_formal": "Semi-formal polite version in target script",
    "casual": "Informal peer version in target script"
  }},
  "predicted_reactions": {{
    "formal_reaction": "How the recipient will perceive this formal version",
    "semi_formal_reaction": "How the recipient will perceive this semi-formal version",
    "casual_reaction": "How the recipient will perceive this casual version"
  }}
}}"""

def get_reply_ghostwriter_prompt(language: str, history: List[MessageTurn], goal: str) -> str:
    transcript = "\n".join([f"{t.speaker}: {t.message}" for t in history])
    return f"""You are an in-chat diplomatic ghostwriter.
Language: {language}
Communicative Goal: {goal}

Context:
{transcript}

Generate a culturally calibrated response that achieves the goal without causing pragmatic friction.
Return ONLY a raw JSON object:
{{
  "suggested_reply": "Culturally calibrated text in native script",
  "diplomatic_rationale": "One sentence explaining why this wording succeeds"
}}"""

def get_speech_translate_prompt(text: str, src_lang: str, tgt_lang: str, tone: str) -> str:
    return f"""You are a bidirectional speech translation engine.

TASK:
Translate the input text from {src_lang} into {tgt_lang}.
DO NOT repeat the text in {src_lang}. The output MUST be in {tgt_lang} and written in its native script.

Input Text ({src_lang}): "{text}"
Target Language: {tgt_lang}
Requested Tone: {tone.upper()}

Tone Directives for {tgt_lang}:
- POLITE: Use formal honorific pronouns (e.g. Hindi: Aap, Tamil: Neenga, Kannada: Neevu, Arabic: Hadratak, English: polite modal verbs like 'could you please').
- TRADITIONAL: Respectful, culturally grounded classical phrasing and idioms.
- CASUAL: Informal/intimate pronouns (e.g. Hindi: Tum/Tu, Tamil: Nee, Kannada: Neenu, Arabic: Inta, English: direct colloquial phrasing).

Return ONLY a raw JSON object with these exact keys:
{{
  "translated_text": "The translated text strictly in {tgt_lang}",
  "t_v_pronoun_used": "Pronoun and level used (e.g. Aap - Formal)",
  "cultural_notes": "One brief sentence explaining why this matches the {tone} tone in {tgt_lang}"
}}"""

def get_chat_reply_prompt(language: str, contact_name: str, contact_role: str, history: List[MessageTurn]) -> str:
    role_styles = {
        "senior": "a senior superior; authoritative, formal, expects deference",
        "peer": "a friendly professional colleague; polite, balanced, semi-formal",
        "junior": "a junior team member; respectful yet casual and eager",
    }
    style = role_styles.get(contact_role, role_styles["peer"])
    transcript = "\n".join([f"{t.speaker}: {t.message}" for t in history])
    return f"""You are roleplaying {contact_name}, {style}, in a workplace chat.
Language: {language} (write in its native script)

Conversation so far:
{transcript}

Write {contact_name}'s next message replying naturally to the last message from "You".
Keep it to 1-2 sentences. Write ONLY as {contact_name}, never as "You".
Return ONLY a raw JSON object:
{{
  "reply": "{contact_name}'s message in native script"
}}"""
