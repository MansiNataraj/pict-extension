# Proactive Intelligent Translation Coach (PITC)

**PITC** is a full-stack, sociopragmatic cross-cultural communication platform designed to prevent relational friction, hierarchy violations, and register mismatches before messages are transmitted. 

It combines real-time pragmatic coaching across multiple organizational roles with a low-latency, bidirectional speech-to-speech translation engine featuring active pragmatic tone calibration.

Supported Language Registers & Scripts:
* **Hindi (`hi`)** — हिन्दी (Devanagari)
* **Tamil (`ta`)** — தமிழ் (Tamil)
* **Kannada (`kn`)** — ಕನ್ನಡ (Kannada)
* **Arabic (`ar`)** — العربية (Arabic)
* **English (`en`)** — Modal politeness (Speech Engine)

---

## Key Features

### 1. Sociopragmatic Text Chat & Pre-Send CRT Guardrail
* **Cultural Risk Taxonomy (CRT):** Automatically evaluates outbound drafts against five sociopragmatic dimensions:
  * **C1: Register / Pronoun Mismatch** ($T/V$ distinction: *Tu* vs. *Tum* vs. *Aap*; *Nee* vs. *Neenga*; *Antum/Hadratak* vs. *Inta*).
  * **C2: Idiomatic Opacity** (Detects literal translations of culture-specific idioms).
  * **C3: Gender Agreement Discordance** (Flags grammatical concord violations).
  * **C4: Hierarchy & Seniority Violations** (Audits deference expected by superiors/elders).
  * **C5: Socio-Cultural & Religious Sensitivities**.
* **Role-Calibrated Workspaces:** Pre-seeded with context-aware session threads across three organizational roles:
  * **Superior / Senior:** High deference (*Formal*).
  * **Peer / Colleague:** Balanced professional collaboration (*Semi-Formal*).
  * **Subordinate / Junior:** Direct, colloquial team interaction (*Informal/Casual*).
* **On-Demand 3-Tone Formality Calibration:** Clicking **"Coach Me"** generates three distinct register options (*Formal*, *Semi-Formal*, *Informal*) with predicted recipient perceptions and one-click draft swapping.
* **Persistent Session Memory:** In-memory message persistence across role switches and home navigation.

### 2. Bidirectional Voice Coach & Speech Engine
* **Native Web Speech STT & TTS:** Leverages browser-native SpeechRecognition and SpeechSynthesis with BCP-47 language routing (`hi-IN`, `ta-IN`, `kn-IN`, `ar-SA`, `en-US`).
* **Pragmatic Tone Presets:** Calibrates spoken translation outputs across **Polite**, **Traditional**, and **Casual** registers.
* **Push-to-Talk (PTT) Dual Speakers:** Dedicated interactive channels for both conversation participants with instant language-swap toggling.
* **Direct Composer Insertion:** One-click handoff from voice translation output directly into the text chat composer.

### 3. Resilient Hybrid AI Inference
* **Primary Cloud Engine:** Direct REST calls to Gemini models (`gemini-2.5-flash-lite`, `gemini-2.5-flash`) via `httpx`.
* **Local Offline Failover:** Automatic fallback to a local Ollama instance running `aya-expanse:8b` during rate-limiting or network disconnections.
* **Robust JSON Extraction:** Token-based payload slicing and ASCII sanitization to prevent parser crashes on structured LLM outputs.

---

## Architecture Overview

```
                      ┌────────────────────────────────────────┐
                      │          React / Vite Frontend         │
                      │               (Port 5173)              │
                      └───────────────────┬────────────────────┘
                                          │
                        REST API (JSON)   │  HTTP / CORS
                                          ▼
                      ┌────────────────────────────────────────┐
                      │          FastAPI Backend Core          │
                      │               (Port 8000)              │
                      ├───────────────────┬────────────────────┤
                      │  /coach           │  /speech-translate │
                      │  /analyse         │  /reply            │
                      └───────────────────┼────────────────────┘
                                          │
                         Provider Routing & Failover
                                          │
                 ┌────────────────────────┴────────────────────────┐
                 ▼                                                 ▼
     ┌───────────────────────┐                         ┌───────────────────────┐
     │  Google Gemini Cloud  │   Fallback on Timeout   │  Local Ollama Engine  │
     │      (Direct REST)    │ ──────────────────────> │    (aya-expanse:8b)   │
     └───────────────────────┘                         └───────────────────────┘
```

---

## Directory Structure

```text
PITC_final/
├── pitc-backend/
│   ├── .env                       # Cloud API key and local model configuration
│   ├── requirements.txt           # Python backend dependencies
│   ├── main.py                    # FastAPI application, CORS, and endpoint mounting
│   ├── config.py                  # Supported languages, CRT rules, and model names
│   └── app/
│       ├── __init__.py
│       ├── chains.py              # Cloud REST execution + Ollama fallback logic
│       ├── models.py              # Pydantic schemas (Request/Response contracts)
│       ├── prompts.py             # CRT diagnostic and speech prompt templates
│       └── routers/
│           ├── __init__.py
│           └── speech.py          # /speech-translate router
│
├── pitc-frontend/
│   ├── package.json               # Node dependencies and build scripts
│   ├── vite.config.js             # Vite configuration
│   ├── tailwind.config.js         # Tailwind CSS styling and animations
│   ├── index.html                 # HTML entry point
│   └── src/
│       ├── App.jsx                # Root component
│       ├── main.jsx               # React DOM initialization
│       ├── index.css              # Global styles & Tailwind utilities
│       └── components/
│           ├── MainPage.jsx       # Landing page, modality picker, and top navbar
│           ├── ChatApp.jsx        # Role-based chat hub & 3-tone CRT coach
│           └── SpeechTranslator.jsx # Bidirectional voice coach with TTS playback
│
├── .gitignore                     # Git exclusion rules (.env, node_modules, .venv)
└── README.md                      # Project documentation
```

---

## Chrome Extension Setup (Quick Start for Testers)

PITC runs as a Chrome side-panel extension (Manifest V3). The extension is only the UI; the FastAPI backend must be running on your own machine at `localhost:8000` whenever you use it. Each tester uses their **own** Gemini API key.

### Requirements
* **Google Chrome** (a recent version with side panel support)
* **Python 3.10+**
* **Node.js 18+** and **npm**
* A **Gemini API key** (free at https://aistudio.google.com/apikey)

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
Check it works: open http://localhost:8000/health in a browser. You should see `{"status":"ok","service":"PITC Backend"}`. Leave this terminal running.

### Step 3: Build the extension
Open a **second** terminal:
```bash
cd PITC-Extension/frontend
npm install
npm run build
```
This creates the folder `frontend/dist`.

### Step 4: Load it in Chrome
1. Go to `chrome://extensions`.
2. Turn on **Developer mode** (top-right toggle).
3. Click **Load unpacked** and select the `frontend/dist` folder.
4. (Optional) Pin the PITC icon from the puzzle-piece menu in the toolbar.
5. Click the **PITC** icon. The side panel opens.

### Step 5: Try it
Follow the [Testing Workflow](#testing-workflow) below.

### Troubleshooting
| Problem | Fix |
|---|---|
| Panel is blank or shows network errors | The backend isn't running. Start it (Step 2) and confirm `/health` works. |
| Coach or translate fails with an AI/auth error | `GEMINI_API_KEY` in `backend/.env` is missing or wrong. Fix it and restart `uvicorn`. |
| `Address already in use` on port 8000 | Another process uses the port. Stop it, or find it with `lsof -i :8000`. |
| Voice (microphone) doesn't work | Speech recognition may be restricted in extension panels. Note the behavior and report it. Text chat is unaffected. |
| Changes to the frontend don't show | Re-run `npm run build`, then click the reload icon on the extension card in `chrome://extensions`. |
| Toolbar icon is a default placeholder | Expected. No custom icons have been added yet. |

> The sections below describe the original web-app setup. For the extension, use the steps above. Directory names there (`pitc-backend`, `pitc-frontend`) correspond to `backend` and `frontend` in this repo.

---

## Installation & Setup

### Prerequisites
* **Python 3.10+**
* **Node.js 18+** & **npm**
* **Google Gemini API Key** (from Google AI Studio)
* *(Optional)* **Ollama** installed with `aya-expanse:8b` for local offline fallback:
  ```bash
  ollama run aya-expanse:8b
  ```

---

### 1. Backend Configuration (`pitc-backend`)

1. Navigate to the backend directory:
   ```bash
   cd pitc-backend
   ```

2. Create and activate a Python virtual environment:
   * **Windows (PowerShell):**
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   * **macOS / Linux:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in `pitc-backend/.env`:
   ```env
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   CLOUD_MODEL_NAME=gemini-2.5-flash-lite
   OLLAMA_BASE_URL=http://localhost:11434/v1
   LOCAL_MODEL_NAME=aya-expanse:8b
   CLOUD_TIMEOUT_SECONDS=10.0
   ```

5. Start the FastAPI development server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```
   *Interactive API documentation is available at `http://localhost:8000/docs`.*

---

### 2. Frontend Configuration (`pitc-frontend`)

1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd pitc-frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the Vite development server:
   ```bash
   npm run dev
   ```
   *The application interface will be live at `http://localhost:5173`.*

---

## API Reference

### Text Chat Endpoints

#### `POST /coach`
Analyzes an outbound message draft against recipient hierarchy and CRT rules, returning three calibrated tone options.
* **Payload:**
  ```json
  {
    "draft_message": "तू कल रिपोर्ट कब देगा?",
    "language_code": "hi",
    "recipient_role": "senior",
    "provider": "auto"
  }
  ```
* **Response:**
  ```json
  {
    "is_risky": true,
    "risk_level": "amber",
    "crt_code": "C1",
    "warning_message": "Using informal pronoun 'तू' (Tu) with a senior manager causes pragmatic friction.",
    "variants": {
      "formal": "आप कल रिपोर्ट किस समय प्रस्तुत करेंगे?",
      "semi_formal": "आप कल रिपोर्ट कब तक दे पाएंगे?",
      "casual": "तू कल रिपोर्ट कब देगा?"
    },
    "predicted_reactions": {
      "formal_reaction": "Perceived as deferential, professional, and respectful of hierarchy.",
      "semi_formal_reaction": "Polite and balanced for daily office collaboration.",
      "casual_reaction": "High risk of causing offense or appearing insubordinate."
    },
    "model_used": "Cloud (gemini-2.5-flash-lite)"
  }
  ```

#### `POST /analyse`
Audits an entire conversational transcript for relational strain and CRT violations.

---

### Speech Translation Endpoints

#### `POST /speech-translate`
Performs bidirectional translation with native script output, honorific tracking, and tone calibration.
* **Payload:**
  ```json
  {
    "audio_text": "Could you please send the updated proposal by this evening?",
    "source_language": "en",
    "target_language": "hi",
    "tone": "polite",
    "provider": "auto"
  }
  ```
* **Response:**
  ```json
  {
    "session_id": "speech-session-default",
    "original_text": "Could you please send the updated proposal by this evening?",
    "translated_text": "क्या आप कृपया आज शाम तक संशोधित प्रस्ताव भेजने का कष्ट करेंगे?",
    "source_language": "en",
    "target_language": "hi",
    "selected_tone": "polite",
    "t_v_pronoun_used": "आप (Aap) - Formal Deference",
    "cultural_notes": "Employs high-deference honorific framing suitable for formal professional requests.",
    "model_used": "Cloud (gemini-2.5-flash-lite)"
  }
  ```

---

## Testing Workflow

1. **Verify Role Awareness:**
   * Select **Text Chat Guardrail** on the landing page.
   * Enter the **Senior / Superior** chat (Dr. Rajesh Sharma).
   * Type an informal Hindi query: `तू फाइल भेज दे`
   * Click **🛡️ Coach Me**. Verify that a **C1** warning appears and the **Formal** card provides the *Aap* honorific variant.
   * Click the **Formal** card to confirm instant draft substitution in the composer.

2. **Verify Bidirectional Speech Engine:**
   * Switch to **Voice Coach** via the top navbar.
   * Set Speaker 1 to **English** and Speaker 2 to **Hindi**; select **Polite** tone.
   * Click **Speak English** and say: *"Let us schedule our project review meeting."*
   * Verify target translation displays in native Devanagari script and plays through synthesized audio.
   * Click **Speak Hindi** and reply in Hindi. Verify the translation translates into spoken English.

3. **Verify Local Fallback:**
   * Disconnect internet access or provide an invalid key in `.env`.
   * Trigger an analysis or voice translation; inspect terminal output to confirm execution routes seamlessly to `Local (aya-expanse:8b)`.

---

## License
MIT License. Developed as an academic capstone for cross-cultural sociopragmatic AI applications.