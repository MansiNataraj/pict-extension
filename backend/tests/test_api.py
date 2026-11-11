"""API tests with the LLM mocked out (no network, no API key needed). Run: pytest"""
import pytest
from fastapi.testclient import TestClient

import main
from app.routers import analyse, chat_reply, coach, crt, reply, speech


async def fake_llm(prompt, temperature=0.2, provider="auto"):
    if "Before translating, decide" in prompt:  # CRT questions prompt
        return {"questions": [
            {"id": "q1", "crt_code": "c1", "question": "Who?", "options": ["a", "b"]},
            {"question": "bad code", "crt_code": "C9", "options": ["x", "y"]},
            {"crt_code": "C2", "question": "one option", "options": ["only"]},
            {"crt_code": "C3", "question": "g", "options": ["m", "f", "x"]},
            {"crt_code": "C4", "question": "third valid, must be cut", "options": ["a", "b"]},
        ]}, "fake"
    if "sociopragmatic translation engine" in prompt:  # CRT translate prompt
        return {"translated_text": "नमस्ते", "register_used": "Aap",
                "crt_applied": [{"code": "c1", "note": "n"}, "junk"],
                "variants": [{"register": "Formal", "text": "x", "nuance": "n"}, {"text": ""}],
                "cultural_notes": "c"}, "fake"
    return {"health_score": "80", "crt_violations": ["C1"], "root_cause": "r", "remediation_advice": "a",
            "suggested_reply": "s", "translated_text": "t", "reply": "r", "is_risky": True}, "fake"


@pytest.fixture()
def client(monkeypatch):
    for mod in (crt, speech, chat_reply, coach, analyse, reply):
        monkeypatch.setattr(mod, "execute_llm_chain", fake_llm)
    return TestClient(main.app)


def test_health(client):
    assert client.get("/health").json() == {"status": "ok", "service": "PITC Backend"}


def test_crt_questions_filters_and_caps(client):
    r = client.post("/crt/questions", json={"text": "Please send the file", "target_language": "hi"})
    assert r.status_code == 200
    qs = r.json()["questions"]
    assert [q["crt_code"] for q in qs] == ["C1", "C3"]


def test_crt_translate_skips_junk(client):
    r = client.post("/crt/translate", json={"text": "hello there", "target_language": "hi", "answers": []})
    body = r.json()
    assert r.status_code == 200
    assert body["translated_text"] == "नमस्ते"
    assert len(body["crt_applied"]) == 1 and len(body["variants"]) == 1


@pytest.mark.parametrize("payload", [
    {"text": "x y", "source_language": "en", "target_language": "en"},   # same language
    {"text": "x y", "target_language": "fr"},                           # unsupported target
    {"text": "x y", "source_language": "fr", "target_language": "hi"},  # unsupported source
    {"text": "   ", "target_language": "hi"},                           # empty
    {"text": "a" * 1501, "target_language": "hi"},                      # too long
])
def test_crt_validation(client, payload):
    assert client.post("/crt/questions", json=payload).status_code == 400
    assert client.post("/crt/translate", json=payload).status_code == 400


def test_crt_translate_empty_model_output_is_502(client, monkeypatch):
    async def empty(*a, **k):
        return {}, "fake"
    monkeypatch.setattr(crt, "execute_llm_chain", empty)
    assert client.post("/crt/translate", json={"text": "hi there", "target_language": "hi"}).status_code == 502


def test_llm_failure_is_500(client, monkeypatch):
    async def boom(*a, **k):
        raise RuntimeError("down")
    monkeypatch.setattr(crt, "execute_llm_chain", boom)
    assert client.post("/crt/questions", json={"text": "hi there", "target_language": "hi"}).status_code == 500


def test_legacy_endpoints(client):
    turn = [{"speaker": "a", "message": "b"}]
    assert client.post("/speech-translate", json={"audio_text": "hi", "source_language": "en", "target_language": "hi"}).status_code == 200
    assert client.post("/chat-reply", json={"contact_name": "A", "conversation_history": turn}).status_code == 200
    assert client.post("/coach", json={"draft_message": "hi"}).status_code == 200
    r = client.post("/analyse", json={"thread": turn})
    assert r.status_code == 200 and r.json()["health_score"] == 80
    assert client.post("/reply", json={"conversation_history": turn, "goal": "g"}).status_code == 200
    assert client.post("/analyse", json={"thread": turn, "language_code": "xx"}).status_code == 400


def test_cors_preflight(client):
    r = client.options("/crt/questions", headers={"Origin": "chrome-extension://x", "Access-Control-Request-Method": "POST"})
    assert r.status_code == 200


def test_json_cleaner():
    from app.chains import clean_and_parse_json
    assert clean_and_parse_json('```json\n{"a": 1}\n```') == {"a": 1}
    assert clean_and_parse_json('noise {"a": 1} tail') == {"a": 1}
    assert clean_and_parse_json("not json") == {}
    assert clean_and_parse_json("") == {}


@pytest.mark.anyio
async def test_cloud_retries_once_on_503(monkeypatch):
    from app import chains
    calls = []

    async def flaky(model, prompt, temperature):
        calls.append(model)
        if len(calls) == 1:
            raise chains.TransientCloudError("HTTP 503")
        return {"ok": True}

    monkeypatch.setattr(chains, "_call_gemini_direct", flaky)
    monkeypatch.setattr(chains, "CLOUD_API_KEY", "k")
    monkeypatch.setattr(chains, "RETRY_DELAY_SECONDS", 0)
    result, model = await chains.execute_llm_chain("p")
    assert result == {"ok": True} and len(calls) == 2 and model.startswith("Cloud")
