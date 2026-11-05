# 🌱 AgriSaathi AI (कृषी साथी AI)

> **Your Smart Farming Companion | शेतकऱ्यांचा विश्वासू डिजिटल साथीदार | किसानों का सच्चा साथी**  
> **Platform Architect & Creator:** **Vishal Sonwane**  
> **GitHub Repository:** [https://github.com/sonwanevishal1361/agri-saathi-ai.git](https://github.com/sonwanevishal1361/agri-saathi-ai.git)

AgriSaathi AI is an enterprise-grade agricultural decision support platform built specifically for Indian farmers, with specialized focus on Maharashtra agriculture. It bridges traditional agronomic science with modern artificial intelligence, providing localized crop advisory, live weather forecasts with spray windows, multi-market APMC mandi price comparisons, government subsidy schemes, crop disease diagnosis, and multi-turn AI advice in **Marathi (मराठी)**, **Hindi (हिंदी)**, and **English**.

The platform is powered by the ultra-fast **Google Gemini API** (`gemini-2.5-flash` / `gemini-1.5-flash` via the official `google-genai` SDK) with optional offline CPU fallback to **Local Ollama** (`qwen2.5:3b`).

---

## 🏗️ System Architecture

```text
+---------------------------------------------------------------------------------+
|                        FARMER & OPERATOR WEB INTERFACE                          |
|             (Streamlit UI - Multilingual: Marathi, Hindi, English)              |
+---------------------------------------------------------------------------------+
        |                        |                             |
        v                        v                             v
+---------------+      +-------------------+      +-------------------------------+
| Farmer Portal |      | Admin & RBAC View |      | Compliance & DPDP 2023        |
| - Crops       |      | - Farmer Directory|      | - Consent Screen              |
| - Weather     |      | - System Metrics  |      | - Privacy Policy Page         |
| - Mandi APMC  |      | - Secure Exports  |      | - Machine-Readable Data (JSON)|
| - Farm Diary  |      | - DB Backups      |      | - Account Erasure Cascades    |
| - Expenses    |      +-------------------+      +-------------------------------+
| - AI Advisor  |                |                             |
+---------------+                |                             |
        |                        |                             |
        +------------------------+-----------------------------+
                                 |
                                 v
+---------------------------------------------------------------------------------+
|                         SERVICE & LOGIC LAYER                                   |
| - UserService (Argon2id, Password Policy, 5-Attempt Lockout, Forced PW Change)   |
| - CropService & ActivityService (Plot Lifecycle, Inputs, Activity Costs)        |
| - ExpenseService & HarvestService (Cultivation Accounting, Net Profit Engine)    |
| - MandiService (Agmarknet Live API, Exponential Retry, Stale Fallback, Net Ret) |
| - ChatService (Gemini Streaming, TF-IDF RAG, Quota Limits, KCC 1800-180-1551)   |
| - BackupService & Health Diagnostic Engine (/health check)                      |
+---------------------------------------------------------------------------------+
        |                                                |
        v                                                v
+--------------------------------+       +----------------------------------------+
|      AI & EXTERNAL PROVIDERS   |       |             DATABASE LAYER             |
| - Google Gemini API (Streaming)|       | - SQLAlchemy 2.x ORM & Pool Management |
| - Local Ollama (Offline CPU)   |       | - Alembic Migration Graph (Batch Ops)  |
| - data.gov.in (Agmarknet API)  |       | - SQLite (Local Development)           |
| - Open-Meteo Weather API       |       | - PostgreSQL (Neon / Supabase / Cloud) |
+--------------------------------+       +----------------------------------------+
```

---

## 📊 Feature Matrix

| Feature Module | Capabilities & Description | Farmer Benefit | Technical Implementation |
|---|---|---|---|
| **Farmer Dashboard** | Mobile-first welcoming agricultural home. Shows local weather, crop status cards, spray window indicators, and rapid action shortcuts. | Understand farm status and navigate to any agricultural feature in under 5 seconds. | Streamlit components, custom CSS themes, session state management. |
| **Multilingual AI Advisor** | Instant agronomic guidance in Marathi, Hindi, and English. Grounded by verified ICAR/CICR research passages. | Reliable farming advice in the farmer's native tongue without complex terminology. | Google Gemini API (`google-genai`), TF-IDF RAG indexing, prompt guardrails. |
| **KCC & KVK Safety Guard** | Automatic detection of pesticide, fungicide, disease, and chemical dosage discussions. Appends official advisories. | Protects farmers against toxic misuse and chemical overdosing. | Automated regex keyword inspection; appends Kisan Call Centre (`1800-180-1551`) and KVK notice. |
| **Mandi Price Comparator** | Real-time multi-market APMC rate analysis. Incorporates road freight, market fees (cess), and loading charges. | Identifies which regional mandi yields highest net profit after transport. | Formula-driven net price calculation; Agmarknet live API with exponential backoff & stale DB cache. |
| **Farm Diary & Activities** | Record tillage, sowing, spraying, weeding, irrigation, fertilizer application, and harvesting with operational costs. | Accurate historical log of all plot treatments and expenditures. | Self-healing schema migrations, foreign key constraints, tenant isolation. |
| **Farm Expense & Profit** | Track expenditures by category (seeds, fertilizer, labor, fuel, machinery). Harvest yield and revenue logging. | Real financial clarity: Net Balance = Total Harvest Revenue - Total Cultivation Expenses. | Aggregation queries, category breakdowns, per-acre investment metrics. |
| **Crop Health Analyzer** | Structured 4-step diagnostic questionnaire for plant disease symptoms with university-backed management steps. | Fast symptom diagnosis for rust, blight, wilt, borer, and sucking pests. | Pillow header byte validation for image uploads; symptom-matching algorithms. |
| **Government Schemes** | Directory of central and Maharashtra state schemes (PM-KISAN, Namo Shetkari, PMFBY, Soil Health Card, e-NAM). | Quick access to subsidy guidelines, eligibility rules, and official application portals. | Static agronomic knowledge database, categorized filters. |
| **Developer Admin Panel** | Protected developer console with Overview KPIs, Farmer Directory, Crop Analytics, Financials, and Audit Logs. | Application owners can monitor adoption and platform health safely. | Role-Based Access Control (`require_admin`), session verification, audit logging. |
| **Authorized Data Exports** | Multi-format exports in CSV (Excel UTF-8 BOM), Excel (.xlsx), and JSON with privacy sanitization. | Research analytics and administrative reporting without risking farmer privacy. | Zero-secret sanitization engine; password hashes and API keys strictly excluded. |
| **DPDP Act 2023 Compliance** | Explicit signup consent, dedicated privacy policy, "Export My Data" JSON download, and account erasure. | Total data sovereignty and legal compliance with Indian privacy laws. | Cascading account deletion, open standard JSON data export, transparent terms. |
| **Security & Rate Limiting** | Strict password policy (8+ chars, upper, lower, digit, special), 5 failed attempts lockout, daily AI query quota. | Defends against brute force attacks and controls cloud API expenses. | Argon2id hashing, lockout timers (`locked_until`), configurable per-user daily limits. |

---

## 📐 Formulas & Agronomic Mathematics (Plain Text)

AgriSaathi AI uses standard, transparent agronomic formulas without complex math formatting:

### 1. Mandi Logistics & Net Return Formula
- Gross Revenue = Modal Price * Quantity
- Transport Cost = (Distance in km / 100) * Transport Rate per 100 km * Quantity
- Market Fee (APMC Cess) = (Modal Price * Market Fee %) / 100 * Quantity
- Loading Charges = Loading Charge per Quintal * Quantity
- Total Logistics Deductions = Transport Cost + Market Fee + Loading Charges
- Net Return = Gross Revenue - Total Logistics Deductions
- Estimated Net Price per Quintal = Net Return / Quantity

### 2. Farm Profitability Formula
- Gross Harvest Revenue = Sum of (Harvested Quantity * Selling Price) across all harvest lots
- Total Cultivation Expenses = Sum of all categorized input and labor expenses
- Net Farm Profit = Gross Harvest Revenue - Total Cultivation Expenses
- Investment per Acre = Total Cultivation Expenses / Total Farm Acreage

### 3. Weather Spray Window Advisory Rules
- If Wind Speed > 15 km/h: Advisory warns against spraying due to chemical drift risk.
- If Precipitation Probability > 40% or Expected Rain > 1.0 mm: Advisory warns to postpone spraying to prevent chemical wash-off.
- If Relative Humidity >= 75%: Advisory warns of elevated fungal infection risks (blight, downy mildew).
- If Wind Speed <= 15 km/h and Rain Probability < 30%: Optimal conditions for foliar applications.

---

## 🗄️ Database Setup: SQLite & PostgreSQL

AgriSaathi AI supports dual database configurations: SQLite for local development and PostgreSQL (Neon, Supabase, AWS RDS, Cloud SQL) for production.

### Local Development (SQLite)
Default setting in `config.py`. SQLite database files are created automatically in `data/agrisaathi.db`.
```ini
DATABASE_URL=sqlite:///./data/agrisaathi.db
```

### Production Setup (PostgreSQL)
Set `DATABASE_URL` in your `.env` file or cloud secrets manager. AgriSaathi AI automatically normalizes connection URLs and sets up connection pooling:
```ini
# Neon Serverless PostgreSQL
DATABASE_URL=postgresql://user:password@ep-cool-sample.us-east-2.aws.neon.tech/agrisaathi?sslmode=require

# Supabase PostgreSQL
DATABASE_URL=postgresql://postgres.yourproject:password@aws-0-ap-south-1.pooler.supabase.com:6543/postgres
```

**Production Pooling Parameters Configured Automatically:**
- `pool_size = 10`: Maintains 10 persistent connections ready for immediate reuse.
- `max_overflow = 20`: Allows up to 20 temporary burst connections during high load.
- `pool_pre_ping = True`: Tests connection health before query execution, preventing stale connection errors.
- `pool_recycle = 300`: Recycles idle connections every 5 minutes to avoid cloud firewall severed socket drops.

### Migrating SQLite Data to PostgreSQL
AgriSaathi AI includes a topological migration tool that transfers all farmer records, crops, expenses, and chats while preserving UUIDs, foreign keys, and password hashes:

```powershell
# Perform a dry run to inspect tables and record counts
python scripts/migrate_sqlite_to_postgres.py --dry-run

# Execute full live migration to PostgreSQL
python scripts/migrate_sqlite_to_postgres.py --postgres-url "postgresql://user:pass@localhost:5432/agrisaathi"
```

### Running Alembic Database Migrations
Alembic migration scripts support both SQLite (via batch mode) and PostgreSQL:
```powershell
# Check current database revision
alembic current

# Upgrade database schema to latest head
alembic upgrade head
```

---

## 🔐 Security & Administrator Provisioning

### Creating the First Administrator Account
Hardcoded credentials have been completely eliminated. Create the first administrator using the provisioning script or environment variables:

```powershell
# Option A: Provision via Interactive CLI
python scripts/create_admin.py --email admin@example.com --password "SecureAdmin@2026!"

# Option B: Provision via Environment Variables
# In .env set:
# ADMIN_EMAIL=admin@example.com
# ADMIN_PASSWORD=SecureAdmin@2026!
python scripts/create_admin.py
```

### Password Policy Requirements
- Minimum 8 characters
- At least one uppercase letter (A-Z)
- At least one lowercase letter (a-z)
- At least one digit (0-9)
- At least one special symbol (`!@#$%^&*()_+-=[]{};':",.<>/?`)

### Rate Limiting & Account Lockout
- After 5 consecutive failed login attempts, the account is temporarily locked for 15 minutes.
- Entering the correct password resets the counter to 0.
- Forced password change on initial login ensures temporary credentials are never retained.

### Per-User Daily AI Quota
- Set `AI_DAILY_REQUEST_LIMIT=25` (or desired number) in `.env`.
- When a farmer reaches their daily limit, the system gracefully delivers a warm, respectful localized message in Marathi, Hindi, or English, while keeping all farm records and market prices fully accessible.

---

## 🚀 Installation & Quickstart

### 1. Clone Repository & Create Virtual Environment
```powershell
cd "$env:USERPROFILE\Desktop\AI-Farming-Assistant"
python -m venv venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

### 2. Install Python Dependencies
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```
Open `.env` and set your configuration:
```ini
AI_PROVIDER=gemini
GEMINI_API_KEY=your_actual_google_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
AI_DAILY_REQUEST_LIMIT=25
```

### 4. Seed Verified Agronomic Knowledge
```powershell
python scripts/seed_knowledge.py
```

### 5. Launch Application
```powershell
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🌐 Production Deployment

### Streamlit Community Cloud
1. Push your repository to GitHub: `https://github.com/<your-username>/agri-saathi-ai`.
2. Visit [share.streamlit.io](https://share.streamlit.io) and create a **New app**.
3. Select your repository, branch `main`, and main file `app.py`.
4. **Select Python 3.12 in Advanced Settings (Critical for Stability):**
   - Click **Advanced settings** (or in app settings after deployment: **App settings -> General / Advanced**).
   - Under **Python version**, select **3.12** from the dropdown menu (AgriSaathi pins this via `runtime.txt` and `.python-version` to guarantee pre-compiled binary wheels for `psycopg`, `pandas`, and `pillow`).
5. In **App settings -> Secrets**, paste your production configuration:
```toml
# Persistent Managed PostgreSQL (Neon, Supabase, AWS RDS, Cloud SQL)
DATABASE_URL = "postgresql://user:password@ep-your-instance.us-east-2.aws.neon.tech/neondb?sslmode=require"

# Google Gemini API
GEMINI_API_KEY = "your_google_gemini_api_key"
GEMINI_MODEL = "gemini-2.5-flash"

# Initial Admin Credentials
ADMIN_EMAIL = "admin@yourdomain.com"
ADMIN_PASSWORD = "YourSecurePassword2026!"
ADMIN_PHONE = "9876543210"

# Application Settings
AI_DAILY_REQUEST_LIMIT = "25"
APP_ENV = "production"
```
6. Click **Deploy / Save**. The application boots, executes `bootstrap_database()`, creates/verifies all tables idempotently, and logs safe connection status without raw passwords.
7. **Verify in Streamlit Cloud Logs:**
   - In your app, click **Manage app** (bottom-right) -> **Logs**.
   - Verify the logs display:
     ```text
     Bootstrapping AgriSaathi database schema...
     Database schema verified. Active tables (13): ['users', 'crops', ...]
     ```
   - If `DATABASE_URL` is configured, verify storage mode indicates `Durable Cloud PostgreSQL`.

### Docker & Docker Compose
Deploy the full stack (AgriSaathi AI + PostgreSQL 16) with a single command:
```bash
# Build and run containers
docker-compose up -d --build

# Inspect logs
docker-compose logs -f app

# Run health diagnostics
curl http://localhost:8501/?health=true
```

### Scheduled Mandi Cache Refresh
To warm the Mandi APMC cache periodically in the background, schedule `scripts/refresh_mandi.py` via cron or Windows Task Scheduler:
```bash
# Example cron entry to refresh prices daily at 6:00 AM
0 6 * * * /app/venv/bin/python /app/scripts/refresh_mandi.py --limit 50
```

---

## 🧪 Automated Testing & Code Quality

AgriSaathi AI includes an extensive automated test suite covering authentication, multi-tenant isolation, crop plot management, farm operations, expense tracking, harvest profitability, multi-market mandi logistics, offline and online AI inference, DPDP compliance, and reliability:

```powershell
# Run the complete test suite
.\venv\Scripts\pytest.exe -v

# Run code style, imports, and security linting with Ruff
.\venv\Scripts\ruff.exe check .
```

All tests execute with simulated database sessions and mocked network adapters, completing in under 35 seconds without consuming live cloud API credits.

---

## 📜 Compliance & Agronomic Support

- **Kisan Call Centre Toll-Free**: `1800-180-1551` (Free government agricultural guidance across India).
- **DPDP Act 2023 Officer**: `privacy@agrisaathi.com`.
- **Agricultural Research Sources**: Indian Council of Agricultural Research (ICAR), Central Institute for Cotton Research (CICR Nagpur), Indian Institute of Soybean Research (IISR Indore), Agmarknet (`agmarknet.gov.in`).

---

*Architected & Crafted with pride by Vishal Sonwane — Creator of AgriSaathi AI.*
