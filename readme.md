# Proactive Intelligent Translation Coach (PITC)

**PITC** is a Chrome/Edge extension that translates selected text on any web page while accounting for sociopragmatic risk: register, honorifics, hierarchy, gender agreement, idioms and cultural sensitivities. Instead of translating blindly, it first asks a few short **Cultural Risk Taxonomy (CRT)** questions and applies your answers to the translation.

Supported languages:
* **Hindi (`hi`)** — हिन्दी (Devanagari)
* **Tamil (`ta`)** — தமிழ் (Tamil)
* **Kannada (`kn`)** — ಕನ್ನಡ (Kannada)
* **Arabic (`ar`)** — العربية (Arabic)
* **English (`en`)**

---

## Key Features

### Select-to-translate with CRT questions
1. Select text (2 to 1500 characters) on any web page, or inside a text box.
2. PITC offers **Translate this with PITC?** and a target-language picker. The source language is detected automatically.
3. PITC asks **at most two** context questions, only when the answer is ambiguous and would change the translation. Each question is tagged with the CRT code it addresses. Neutral text gets no questions, and you can always click **Skip questions**.
4. You receive the translation, the register used, a note per CRT dimension that was applied, and **Formal / Semi-formal / Casual** variants with **Copy** buttons.

### Cultural Risk Taxonomy (CRT)
* **C1: Register / pronoun level** (*Tu / Tum / Aap*, *Nee / Neenga*, *Neenu / Neevu*, *Inta / Hadratak*).
* **C2: Idiomatic opacity** (literal translations of culture-specific idioms).
* **C3: Gender agreement** (verb and pronoun concord).
* **C4: Hierarchy and seniority** (deference owed to seniors, elders, clients).
* **C5: Socio-cultural and religious sensitivity.**

### Resilient hybrid AI inference
* **Primary:** Gemini via direct REST (`httpx`), trying the configured model and then fallbacks.
* **Local failover:** a local Ollama instance (`aya-expanse:8b`) when the cloud is unavailable.
* **Robust JSON extraction** and input validation so malformed model output does not crash the API.
* **Logging:** every request, answer, model choice and failure reason is written to `backend/pitc.log`.

> The repo also contains a React chat-coach and voice-translator UI plus the `/coach`, `/analyse`, `/reply` and `/speech-translate` endpoints from the original web app. The extension does not currently expose them.

---

## Architecture Overview

```
  Web page ── selected text ──► content script (popup UI, shadow DOM)
                                      │  chrome.runtime message
                                      ▼
                         background service worker
                                      │  fetch (localhost:8000)
                                      ▼
                         ┌──────────────────────────┐
                         │   FastAPI backend        │
                         │   POST /crt/questions    │
                         │   POST /crt/translate    │
                         └────────────┬─────────────┘
                                      │ provider routing + failover
                        ┌─────────────┴─────────────┐
                        ▼                           ▼
               Google Gemini (REST)   ──►   Local Ollama (fallback)
```

The extension is only the UI. The backend runs on the user's own machine and holds the API key.

---

## Directory Structure

```text
PITC-Extension/
├── backend/
│   ├── .env.example               # Copy to .env and add GEMINI_API_KEY
│   ├── requirements.txt
│   ├── main.py                    # FastAPI app, CORS, request logging
│   ├── config.py                  # Languages, CRT taxonomy, model names
│   └── app/
│       ├── chains.py              # Gemini call + Ollama fallback, logging
│       ├── models.py              # Pydantic request/response schemas
│       ├── prompts.py             # CRT question + translation prompts
│       ├── logging_config.py      # Console + backend/pitc.log
│       └── routers/
│           ├── crt.py             # /crt/questions, /crt/translate (used by the extension)
│           └── speech.py, chat_reply.py, ...   # legacy web-app endpoints
│
├── frontend/
│   ├── public/
│   │   ├── manifest.json          # Manifest V3
│   │   ├── content.js             # Select-to-translate popup
│   │   └── background.js          # Service worker, relays requests to the backend
│   ├── src/                       # Legacy React UI (not exposed by the extension)
│   └── vite.config.js             # Builds to frontend/dist
│
└── readme.md
```

---

## Chrome / Edge Extension Setup (Quick Start for Testers)

The extension is only the UI; the FastAPI backend must be running on your own machine at `localhost:8000` whenever you use it. Each tester uses their **own** Gemini API key.

### Requirements
* **Google Chrome** or **Microsoft Edge** (Chromium, Manifest V3)
* **Python 3.10+**
* **Node.js 18+** and **npm**
* A **Gemini API key** (free at https://aistudio.google.com/apikey)
* *(Optional)* **Ollama** with `aya-expanse:8b` for offline fallback: `ollama run aya-expanse:8b`

### Step 1: Get the code
```bash
git clone https://github.com/MansiNataraj/pict-extension.git
cd pict-extension
```

### Step 2: Start the backend
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate          # Windows PowerShell: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env               # Windows PowerShell: Copy-Item .env.example .env
```
Open `backend/.env` and replace `your_gemini_api_key_here` with your own key. Then start the server:
```bash
uvicorn main:app --port 8000
```
Check it works: open http://localhost:8000/health. You should see `{"status":"ok","service":"PITC Backend"}`. Leave this terminal running. Interactive API docs are at http://localhost:8000/docs.

### Step 3: Build the extension
Open a **second** terminal:
```bash
cd pict-extension/frontend
npm install
npm run build
```
This creates the folder `frontend/dist`.

### Step 4: Load it in the browser
1. Go to `chrome://extensions` (Edge: `edge://extensions`).
2. Turn on **Developer mode**.
3. Click **Load unpacked** and select the `frontend/dist` folder.
4. Refresh any page that was already open. Pages open before the install do not get the extension.

There is no toolbar panel: the extension works by selecting text on a page.

### Step 5: Try it
Open any normal web page (not a `chrome://` page or the Chrome Web Store) and select some text.
1. A small box asks **Translate this with PITC?**. Pick the target language and click **Translate**.
2. Answer the CRT questions, or click **Skip questions**.
3. Check the translation, the register used, the CRT notes and the three register variants.

### Where the logs are (send these when reporting a problem)
| Log | How to open it |
|---|---|
| Backend | `backend/pitc.log` (also printed in the terminal running `uvicorn`). Shows each request, the questions asked, the answers, which model replied, timings, and the exact Gemini error if a call fails. |
| Extension background | `chrome://extensions` -> PITC -> click the **service worker** link -> Console. Lines start with `[PITC bg]`. |
| Page popup | On the page where you selected text: right click -> Inspect -> Console. Lines start with `[PITC]`. |

Set `PITC_LOG_LEVEL=DEBUG` before starting the backend for more detail.

### Troubleshooting
| Problem | Fix |
|---|---|
| No popup appears when selecting text | Reload the extension on `chrome://extensions`, then refresh the page. It does not run on `chrome://` pages, the Web Store, or PDF viewers. |
| "Cannot reach the PITC backend at localhost:8000" | The backend isn't running. Start it (Step 2) and confirm `/health` works. |
| "GEMINI_API_KEY is not set" | Create `backend/.env` from `.env.example`, add your key, and restart `uvicorn` (the file is only read at startup). |
| "All AI providers failed" | Open `backend/pitc.log` and read the `Cloud ... failed` lines. Typical causes are an invalid key, a model name your key can't use, or quota limits. |
| `Address already in use` on port 8000 | Another process uses the port. Find it with `lsof -i :8000` and stop it. |
| Popup appears in the wrong place inside a text box | Report it with the site name. |
| Frontend changes don't show | Re-run `npm run build`, click the reload icon on the extension card, and refresh the page. |

---

## API Reference

### `POST /crt/questions`
Returns the CRT context questions (0 to 2) that should be answered before translating.
```json
{ "text": "Please send the file today.", "source_language": "auto", "target_language": "hi" }
```
```json
{
  "questions": [
    { "id": "q1", "crt_code": "C4", "question": "Who is this message for?",
      "options": ["A senior or elder", "A colleague", "A junior or close friend"] }
  ],
  "model_used": "Cloud (gemini-...)"
}
```

### `POST /crt/translate`
Translates using the answers. `answers` may be empty (the model then picks a safe, polite default).
```json
{
  "text": "Please send the file today.",
  "source_language": "auto",
  "target_language": "hi",
  "answers": [{ "id": "q1", "crt_code": "C4", "question": "Who is this message for?", "answer": "A senior or elder" }]
}
```
Response fields: `translated_text`, `register_used`, `crt_applied` (list of `{code, note}`), `variants` (list of `{label, text, nuance}`), `cultural_notes`, `model_used`.

Limits: text is 1 to 1500 characters; `source_language` is `auto` or one of `en, hi, ta, kn, ar`; source and target must differ.

### Legacy endpoints (original web app, not used by the extension)
`POST /coach`, `POST /analyse`, `POST /reply`, `POST /speech-translate`, `POST /chat-reply`. See `http://localhost:8000/docs`.

---

## Testing Workflow

1. **CRT questions affect the output**
   * Select `Please send me the report by tomorrow.`, target **Hindi**.
   * Answer the recipient question with **A senior or elder**. Expect the *Aap* register and a C1 or C4 note.
   * Select the same text again and answer **A junior or close friend**. Expect a more informal register, so the two translations should differ.
2. **No questions for neutral text**
   * Select `The meeting is at 3 PM.` PITC may go straight to the translation.
3. **Skip questions**
   * Click **Skip questions** and confirm a translation still appears with a neutral, polite register.
4. **Error handling**
   * Stop the backend and select text. The popup should say it cannot reach the backend.
   * Start the backend with no `.env` and expect the "GEMINI_API_KEY is not set" message.
   * With the key set, check that `backend/pitc.log` shows `Cloud ... OK` and which model answered.
5. **Local fallback (optional)**
   * Use an invalid key with Ollama running. The log should show the cloud failures and then `Ollama OK`.

---

## License
MIT License. Developed as an academic capstone for cross-cultural sociopragmatic AI applications.
