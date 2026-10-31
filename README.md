# 🌱 AgriSaathi AI (कृषी साथी AI)
> **Your Smart Farming Companion | शेतकऱ्यांचा विश्वासू डिजिटल साथीदार | किसानों का सच्चा साथी**  
> **Platform Architect & Creator:** **Vishal Sonwane**  
> **GitHub Repository:** [https://github.com/sonwanevishal1361/agri-saathi-ai.git](https://github.com/sonwanevishal1361/agri-saathi-ai.git)

AgriSaathi AI is a comprehensive, production-grade agricultural assistance platform designed specifically for Indian farmers. It bridges traditional agronomic science with modern artificial intelligence, empowering farmers with verified crop guides, real-time weather forecasts with spray advisories, multi-market APMC mandi price comparisons, government subsidy schemes, interactive symptom diagnosis, and multi-turn AI advice in **Marathi (मराठी)**, **Hindi (हिंदी)**, and **English**.

Powered primarily by the ultra-fast **Google Gemini API** (`gemini-3.5-flash-lite` via the official `google-genai` SDK), with optional offline CPU fallback to **Local Ollama** (`qwen2.5:3b`).

> [!TIP]
> **Complete Technical Documentation**: For the exhaustive architectural blueprint, ER diagrams, schema reference, and deployment procedures, see [DOCUMENTATION.md](DOCUMENTATION.md).

---

## 🌾 Core Capabilities

1. **Farmer-Friendly Companion Dashboard**:
   - Clean, welcoming agricultural interface designed for rural farmers.
   - Live weather guidance translating wind and precipitation into practical spray advisories.
   - Crop cards tracking variety, sowing date, acreage, and stage-specific care advice.
   - Quick action shortcuts to all core farming tools.

2. **Multi-Market APMC Price Comparison (Agmarknet)**:
   - Integrates live Government of India Agmarknet data (`data.gov.in`).
   - Evaluates road freight and ranks APMC mandis by **estimated net return (₹/Quintal)**.
   - Displays modal, minimum, and maximum prices with clear data freshness tags.

3. **Multilingual AI Agronomist (Google Gemini)**:
   - Fast (<2s) context-aware streaming inference powered by `gemini-3.5-flash-lite`.
   - Native support for Marathi (`mr`), Hindi (`hi`), and English (`en`).
   - Bounded multi-turn conversational memory with strict tenant isolation.
   - Built-in guardrails against dangerous or fabricated pesticide dosages.

4. **Agricultural Knowledge Retrieval (Lightweight TF-IDF RAG)**:
   - Grounded in verified packages of practices from ICAR, CICR Nagpur, and IISR Indore.
   - Transparent citations with official research institute titles and portal links.

5. **Crop Lifecycle & Plot Management**:
   - Tracks plots across 6 agronomic stages: Sowing, Vegetative, Flowering, Pod/Boll Development, Maturity, and Harvesting.

6. **Farm Diary & Field Operations**:
   - Digital log for weeding, spraying, fertilizing, irrigation, pruning, and harvesting.
   - Tracks inputs, products, quantities, and operational costs.
   - Equipped with **self-healing automatic schema migration**.

7. **Farm Expenses & Financial Tracking**:
   - Input cost tracking across seeds, fertilizers, pesticides, labor, diesel, machinery rentals, and transport.
   - Real-time financial metrics and investment per acre.

8. **Harvest Records & Net Profitability**:
   - Log harvested quantities, units (Quintal, Tonne, Kg), and selling prices.
   - Real net balance: $\text{Total Harvest Revenue} - \text{Cultivation Expenses}$.

9. **Crop Health & Symptom Analyzer**:
   - Secure image upload (JPG, PNG validated via Pillow magic bytes).
   - Structured 4-step diagnostic questionnaire with agricultural university guidelines.

10. **Government Agricultural Schemes Directory**:
    - Verified central and Maharashtra state schemes (PM-KISAN, Namo Shetkari, PMFBY, Soil Health Card, PMKSY, KCC, e-NAM).
    - Clear eligibility criteria and direct links to official application portals.

11. **Developer Admin Panel & Data Management**:
    - Role-Based Access Control (RBAC) isolating admin operations from standard farmers.
    - 9-tab dashboard: Overview KPIs, Farmer Directory, Crop Analytics, Activity Trends, Financial Health, AI Topics, Data Exports, Backups, and Audit Logs.
    - Multi-format authorized exports in **CSV** (UTF-8 BOM for Excel), **Excel (.xlsx)**, and **JSON**.
    - Live atomic SQLite backups and pre-restore safety snapshots.

12. **Production PostgreSQL Migration Engine**:
    - Topological table migration CLI (`scripts/migrate_sqlite_to_postgres.py`) preserving all UUIDs, timestamps, and relationships.

---

## 🛠️ Developer Administrator Login

AgriSaathi AI includes a dedicated administrator login for application owners:
- **Email:** `admin@agrisaathi.com`
- **Password:** `Admin@Agri2026!`
- **Access Route:** Login screen $\rightarrow$ 3rd tab: **`🛠️ ॲडमिन (Admin Login)`**.

*(Configurable via `ADMIN_DEFAULT_EMAIL` and `ADMIN_DEFAULT_PASSWORD` in `.env`).*

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

### 4. Configure Gemini API Key
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

### 5. Initialize Database & Seed Verified Agronomic Knowledge
```powershell
python scripts/seed_knowledge.py
```

### 6. Run the Application
Launch the AgriSaathi AI interface:
```powershell
streamlit run app.py
```
The app will open automatically in your browser at `http://localhost:8501`.

---

## 🧪 Automated Testing & Code Quality

AgriSaathi AI comes with an exhaustive test suite of **101 automated Pytest tests** covering authentication, tenant isolation, crop management, farm diary, expense tracking, mandi comparisons, weather advisories, admin RBAC, and data exports:

```powershell
# Run the complete test suite
.\venv\Scripts\pytest.exe -v

# Run code quality and linting checks with Ruff
.\venv\Scripts\ruff.exe check .
```

All 101 tests pass cleanly without network calls, executing in $<30\text{ seconds}$.

---

## 🔒 Security & Privacy Notice

- **No Plaintext Passwords**: All farmer and administrator passwords are encrypted using **Argon2id**.
- **Multi-Tenant Data Isolation**: Database queries enforce ownership checks at the service layer, preventing cross-farmer access.
- **Zero-Secret Export Guarantee**: All exported CSV, Excel, and JSON files strip passwords, hashes, tokens, and API keys.
- **Upload Hardening**: File uploads are restricted to `.jpg`, `.jpeg`, and `.png` under 5MB with Pillow magic-byte header validation.

---

*Authored by Vishal Sonwane — Platform Architect & Creator of AgriSaathi AI.*
