# 🌱 AgriSaathi AI (कृषी साथी AI)
> **Your Smart Farming Companion | शेतकऱ्यांचा विश्वासू डिजिटल साथीदार | किसानों का सच्चा साथी**  
> **Platform Architect & Creator:** **Vishal Sonwane**

AgriSaathi AI is a comprehensive, production-grade agricultural assistance platform designed specifically for Indian farmers. It bridges traditional agronomic science with modern artificial intelligence, empowering farmers with verified crop guides, real-time weather forecasts, APMC mandi market rates, government subsidy schemes, interactive symptom diagnosis, and multi-turn AI advice in **Marathi**, **Hindi**, and **English**.

Powered primarily by the ultra-fast **Google Gemini API** (`gemini-3.5-flash-lite` via the official `google-genai` SDK), with optional offline CPU fallback to **Local Ollama** (`qwen2.5:3b`).

---

## 🌾 Core Features

1. **Farmer Account & Profile**:
   - Secure Argon2id password hashing and session management.
   - Farm profile tracking (state, district, village, acreage, soil classification, irrigation type).
   - Strict per-tenant authorization preventing any cross-farmer data access.

2. **Crop Lifecycle Management**:
   - Track active and harvested crops (sowing date, expected harvest, growth stage, plot name).
   - Growth stages: Sowing, Vegetative, Flowering, Boll/Pod Formation, Ripening, Harvesting.

3. **Farm Diary & Activities**:
   - Digital log for weeding, spraying, fertilizing, irrigation, pruning, and harvesting.
   - Linked to specific crop plots or general farm operations.

4. **Farm Expenses & Financial Tracking**:
   - Track input costs across seeds, fertilizers, pesticides, labor, diesel, machinery rentals, and transport.
   - Categorical breakdown and visual financial metrics.

5. **Harvest Records & Net Balance**:
   - Log harvested quantities, units (Quintal, Tonne, Kg), selling prices, and buyer APMC markets.
   - Real profit calculations: Total Harvest Revenue minus Recorded Crop Expenses.

6. **Primary Cloud AI Advisor (Google Gemini API)**:
   - Ultra-fast (<2s) context-aware streaming inference powered by `gemini-3.5-flash-lite` using the official `google-genai` SDK.
   - Multilingual response preferences: Marathi (`mr`), Hindi (`hi`), English (`en`).
   - Bounded multi-turn conversation memory with strict tenant data isolation.
   - Handles network timeouts, quota limits, and API errors gracefully.

7. **Optional Offline AI Fallback (Local Ollama)**:
   - Optional fallback controlled by `ENABLE_OLLAMA_FALLBACK=true` (or standalone mode via `AI_PROVIDER=ollama`).
   - Powered by `qwen2.5:3b` running on local CPU via `ollama serve`.

8. **Agricultural Knowledge Retrieval (Lightweight TF-IDF RAG)**:
   - Grounded in verified packages of practices from ICAR, CICR Nagpur, IISR Indore, and State Agricultural Universities.
   - Transparent citations: Displays official institute titles and portal links.
   - Prompt injection guardrails: Untrusted reference material boundaries.
   - Strict safety instructions against fabricating chemical pesticide dosages.

9. **Crop Health & Symptom Analyzer**:
   - Upload crop leaf/stem/fruit photos (JPG, PNG validated via Pillow magic bytes).
   - Symptom questionnaire for localized diagnosis with university guidelines.
   - Honest transparency notice: local text model does not claim automated vision inference.

10. **Live Weather & Agricultural Advisories**:
    - Integrated with Open-Meteo API for real-time district forecasts across India.
    - Current weather (temp, humidity, rain, wind) + 5-day forecast.
    - Uncertainty-aware spray postponement and irrigation alerts.

11. **APMC Mandi Market Prices**:
    - Agmarknet verified benchmark rates for major Indian crops across state mandis.
    - Transparent data mode labeling (Benchmark vs Live API).
    - Modal price, min/max prices, and official portal links (`https://agmarknet.gov.in/`).

12. **Government Agricultural Schemes**:
    - Verified central and state schemes (PM-KISAN, PMFBY, Soil Health Card, PMKSY, KCC, e-NAM, Namo Shetkari).
    - Clear eligibility summaries, subsidy benefits, and direct links to official application portals.

---

## 🚀 Windows PowerShell Quickstart Guide

### 1. Open PowerShell and Navigate to Project
```powershell
cd "$env:USERPROFILE\Desktop\AI-Farming-Assistant"
```

### 2. Create and Activate Virtual Environment
```powershell
python -m venv venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Gemini API Key & Environment
You can configure your `GEMINI_API_KEY` either via `.env` or directly in PowerShell.

#### Option A: Using `.env` file (Recommended for development)
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```
Open `.env` in your text editor and set:
```ini
AI_PROVIDER=gemini
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_MODEL=gemini-3.5-flash-lite
ENABLE_OLLAMA_FALLBACK=false
```
*(Note: `.env` is listed in `.gitignore` and is never committed to Git).*

#### Option B: Set Environment Variable in PowerShell (Session-only)
```powershell
$env:GEMINI_API_KEY = "your_actual_gemini_api_key_here"
$env:AI_PROVIDER = "gemini"
```

### 5. Initialize Database & Seed Verified Agronomic Knowledge
```powershell
# Initialize SQLite database and seed verified ICAR crop knowledge & RAG documents
python scripts/seed_knowledge.py
```

### 6. (Optional) Local Ollama Fallback
If you wish to enable offline Ollama fallback:
```powershell
# Set ENABLE_OLLAMA_FALLBACK=true in .env, then in a separate terminal:
ollama serve
ollama pull qwen2.5:3b
```

### 7. Run the Application
Launch the AgriSaathi AI Streamlit interface:
```powershell
streamlit run app.py
```
The app will open automatically in your browser at `http://localhost:8501`.

---

## 🧪 Running Automated Tests & Code Quality Checks

Execute all 61 automated Pytest unit and integration tests (tests use mocked responses and do not make live paid API calls):
```powershell
python -m pytest -v
```

Run code quality and linting checks with Ruff:
```powershell
python -m ruff check .
```

---

## 🏛️ Project Architecture

```
AI-Farming-Assistant/
├── app.py                      # Streamlit application entrypoint & routing
├── config.py                   # Pydantic Settings & environment config (Gemini & Ollama)
├── requirements.txt            # Python dependencies (includes google-genai)
├── pyproject.toml              # Ruff and packaging configuration
├── alembic.ini                 # Database migration configuration
├── README.md                   # Beginner-friendly documentation
├── .env.example                # Example environment template (no real keys)
│
├── core/                       # Core system utilities
│   ├── auth.py                 # Farmer session identity & ownership guardrails
│   ├── database.py             # SQLAlchemy 2.x engine & session management
│   ├── exceptions.py           # Application exception hierarchy (includes ConfigurationError)
│   └── security.py             # Argon2id password hashing & tokens
│
├── models/                     # SQLAlchemy database models
│   ├── user.py                 # Farmer account & profile
│   ├── crop.py                 # Crops & growth stages
│   ├── activity.py             # Farm diary operations
│   ├── expense.py              # Categorized farm expenses
│   ├── harvest.py              # Harvest yields & sales revenue
│   ├── conversation.py         # AI conversations & messages
│   ├── knowledge.py            # Verified crop knowledge & RAG docs
│   └── health_observation.py   # Crop symptom checks & photo storage
│
├── schemas/                    # Pydantic validation schemas
│   ├── user.py
│   ├── crop.py
│   ├── activity.py
│   ├── expense.py
│   ├── harvest.py
│   └── chat.py
│
├── services/                   # Business logic layer
│   ├── user_service.py         # Registration, login, profile, password change
│   ├── crop_service.py         # Crop CRUD with multi-tenant isolation
│   ├── activity_service.py     # Farm activities logging
│   ├── expense_service.py      # Expense tracking & summary calculations
│   ├── harvest_service.py      # Harvest yields & net profit calculation
│   ├── gemini_service.py       # Google Gen AI SDK integration (streaming & non-streaming)
│   ├── ollama_service.py       # Ollama HTTP API client (optional offline fallback)
│   ├── chat_service.py         # Multi-provider routing, RAG context & bounded history
│   ├── knowledge_service.py    # TF-IDF RAG retrieval & crop library
│   ├── weather_service.py      # Open-Meteo live forecasts & advisories
│   ├── mandi_service.py        # Agmarknet market prices
│   ├── schemes_service.py      # Government schemes & portal directory
│   └── image_service.py        # Crop photo upload & symptom questionnaire
│
├── ui/                         # Streamlit UI presentation layer
│   ├── state.py                # Session state management
│   ├── auth_pages.py           # Login & registration tabs
│   ├── dashboard.py            # Overview metrics, quick actions & shortcuts
│   ├── crops_page.py           # Crop management (active & harvested)
│   ├── crop_detail.py          # Crop timeline, activities, expenses & harvest
│   ├── chat_page.py            # Interactive multilingual AI chatbot with live streaming
│   ├── diary_page.py           # Farm activity diary
│   ├── expenses_page.py        # Farm expense logger & category breakdown
│   ├── harvest_page.py         # Harvest yields, selling rates & net profit
│   ├── weather_page.py         # Weather cards & agricultural advisory
│   ├── market_page.py          # APMC mandi rates search
│   ├── schemes_page.py         # Welfare schemes explorer
│   ├── image_page.py           # Crop disease symptom diagnosis
│   └── profile_page.py         # Profile update, security & account deletion
│
├── utils/                      # Helper utilities
│   ├── formatting.py           # Indian Rupee (INR) and date formatting
│   ├── language.py             # Multilingual dictionary (mr, hi, en)
│   ├── logging_config.py       # Structured logging with Windows UTF-8 safety
│   ├── prompts.py              # Context-aware agricultural system prompts
│   └── validation.py           # File extension, size & header security checks
│
├── scripts/                    # Management scripts
│   ├── init_db.py              # Initialize SQLite tables
│   └── seed_knowledge.py      # Seed verified ICAR crop library & RAG passages
│
├── migrations/                 # Alembic database migration versions
│   ├── env.py
│   └── versions/
│
└── tests/                      # Automated Pytest suite (61 tests)
    ├── conftest.py
    ├── test_auth.py
    ├── test_authorization.py
    ├── test_crops.py
    ├── test_activities.py
    ├── test_expenses.py
    ├── test_harvest.py
    ├── test_gemini.py          # Google Gemini SDK unit tests (mocked)
    ├── test_chat.py            # Chat routing, streaming, and fallback tests
    ├── test_knowledge.py
    ├── test_safety.py
    ├── test_services.py
    └── test_uploads.py
```

---

## 🔒 Security & Privacy Notice

- **API Keys & Secrets**: The `GEMINI_API_KEY` is loaded securely via Pydantic settings and environment variables. The `.env` file is excluded from version control via `.gitignore`. Real credentials are never hardcoded or printed to stdout.
- **No Plaintext Passwords**: All farmer passwords are protected using the memory-hard **Argon2id** algorithm.
- **Tenant Isolation**: Every database query verifies that the requesting farmer's ID matches the resource owner. Attempting to query, update, or delete another farmer's data immediately triggers `AuthorizationError`.
- **Upload Hardening**: File uploads are restricted to `.jpg`, `.jpeg`, and `.png` under 5MB. Byte headers are verified using Pillow to reject renamed malicious binaries, and filenames are sanitized against path traversal attacks.
